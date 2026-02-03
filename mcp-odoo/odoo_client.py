# odoo_client.py

import os

#Load environment variables from .env into this Python process.
from dotenv import load_dotenv
load_dotenv()

import logging
import xmlrpc.client
from typing import List, Dict, Any


# ------------------------------------------------------------------------------
# Logging configuration
# ------------------------------------------------------------------------------

logger = logging.getLogger("odoo_client")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
formatter = logging.Formatter(
    "[ODOO_CLIENT] %(asctime)s | %(levelname)s | %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)


# ------------------------------------------------------------------------------
# Exceptions (fail loudly, fail clearly)
# ------------------------------------------------------------------------------

class OdooClientError(Exception):
    pass


class ValidationError(OdooClientError):
    pass


class PermissionError(OdooClientError):
    pass


# ------------------------------------------------------------------------------
# Odoo Client
# ------------------------------------------------------------------------------

class OdooClient:
    """
    The ONLY component allowed to talk to Odoo.

    Responsibilities:
    - Authentication
    - Safe read/write primitives
    - Enforcing execution constraints
    - Logging every operation
    """

    MAX_RECORDS = 100

    def __init__(self):
        self.url = os.getenv("ODOO_URL")
        self.db = os.getenv("ODOO_DB")
        self.username = os.getenv("ODOO_USERNAME")
        self.password = os.getenv("ODOO_PASSWORD")

        if not all([self.url, self.db, self.username, self.password]):
            raise OdooClientError(
                "Missing Odoo credentials. "
                "Ensure ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD are set."
            )

        self.common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")
        self.models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")

        self.uid = self._authenticate()
        self.company_id = self._get_current_company()


    # --------------------------------------------------------------------------
    # Authentication & context
    # --------------------------------------------------------------------------

    def _authenticate(self) -> int:
        uid = self.common.authenticate(
            self.db, self.username, self.password, {}
        )
        if not uid:
            raise OdooClientError("Authentication with Odoo failed.")
        logger.info("Authenticated with Odoo (uid=%s)", uid)
        return uid

    # def _get_current_company(self) -> int:
    #     user_data = self.search_read(
    #         model="res.users",
    #         domain=[("id", "=", self.uid)],
    #         fields=["company_id"],
    #         limit=1,
    #     )
    #     if not user_data or not user_data[0].get("company_id"):
    #         raise OdooClientError("Unable to determine current company.")
    #     company_id = user_data[0]["company_id"][0]
    #     logger.info("Operating in company_id=%s", company_id)
    #     return company_id

    def _get_current_company(self) -> int:
        """
        Fetch the current user's company WITHOUT applying company scoping.
        This is part of bootstrap and must bypass search_read.
        """
        user_data = self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            "res.users",
            "read",
            [[self.uid]],
            {"fields": ["company_id"]},
        )

        if not user_data or not user_data[0].get("company_id"):
            raise OdooClientError("Unable to determine current company.")

        company_id = user_data[0]["company_id"][0]
        logger.info("Operating in company_id=%s", company_id)
        return company_id


    # --------------------------------------------------------------------------
    # Public SAFE primitives
    # --------------------------------------------------------------------------

    def search_read(
        self,
        model: str,
        domain: List,
        fields: List[str],
        limit: int = 10,
        offset: int = 0,
        apply_company_scope: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Safe read operation.
        Used by ALL read tools.
        """

        self._validate_limit(limit)
        self._validate_domain(domain)
        self._validate_fields(fields)

        if apply_company_scope:
            domain = self._apply_company_scope(domain, model)

        self._log_operation(
            model=model,
            operation="read",
            domain=domain,
            fields=fields,
            limit=limit,
        )

        return self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            model,
            "search_read",
            [domain],
            {
                "fields": fields,
                "limit": limit,
                "offset": offset,
            },
        )

    def create(self, model: str, values: Dict[str, Any]) -> int:
        """
        Safe create operation.
        Used ONLY by allowed create tools.
        """

        self._validate_create_values(values)

        # Force company scoping
        if "company_id" in values:
            raise ValidationError("company_id cannot be set manually.")

        values["company_id"] = self.company_id

        self._log_operation(
            model=model,
            operation="create",
            values=values,
        )

        return self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            model,
            "create",
            [values],
        )

    def write(
        self,
        model: str,
        record_id: int,
        values: Dict[str, Any],
    ) -> bool:
        """
        Safe write operation.
        ONLY allowed for crm.lead.stage_id updates.
        """

        if model != "crm.lead":
            raise PermissionError("Write operations are forbidden for this model.")

        if list(values.keys()) != ["stage_id"]:
            raise PermissionError(
                "Only stage_id update is allowed for crm.lead."
            )

        self._log_operation(
            model=model,
            operation="write",
            record_id=record_id,
            values=values,
        )

        return self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            model,
            "write",
            [[record_id], values],
        )

    # --------------------------------------------------------------------------
    # Validation helpers
    # --------------------------------------------------------------------------

    def _validate_limit(self, limit: int):
        if limit <= 0 or limit > self.MAX_RECORDS:
            raise ValidationError(
                f"Limit must be between 1 and {self.MAX_RECORDS}."
            )

    def _validate_domain(self, domain: List):
        if not isinstance(domain, list):
            raise ValidationError("Domain must be a list.")
        if domain == []:
            raise ValidationError("Empty domain (full table scan) is forbidden.")

    def _validate_fields(self, fields: List[str]):
        if not fields:
            raise ValidationError("Field list cannot be empty.")
        for field in fields:
            if not isinstance(field, str):
                raise ValidationError("Invalid field name.")

    def _validate_create_values(self, values: Dict[str, Any]):
        if not isinstance(values, dict) or not values:
            raise ValidationError("Create values must be a non-empty dictionary.")

    # --------------------------------------------------------------------------
    # Company scoping
    # --------------------------------------------------------------------------

    def _apply_company_scope(self, domain: List, model: str) -> List:
        """
        Enforce company scoping ONLY for models that support company_id.
        """

        MODELS_WITHOUT_COMPANY_ID = {
            "hr.attendance",
        }

        if model in MODELS_WITHOUT_COMPANY_ID:
            return domain

        company_domain = [
            "|",
            ("company_id", "=", self.company_id),
            ("company_id", "=", False),
        ]

        return domain + company_domain


    # --------------------------------------------------------------------------
    # Logging
    # --------------------------------------------------------------------------

    def _log_operation(self, **kwargs):
        logger.info("ODOO OPERATION | %s", kwargs)
