from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView
from django.conf import settings

from .models import Warehouse, ShippingRequest
from .serializers import ShippingInputSerializer, ShippingRequestSerializer, WarehouseSerializer
import requests
from requests.exceptions import ConnectionError, Timeout, RequestException
import logging

logger = logging.getLogger(__name__)


class ShippingRateAPIView(APIView):
    """
    POST:
    Accepts user destination address.
    Uses stored warehouse origin to call Easyship API.
    Returns shipping rate and tax info for FedEx, UPS, and USPS only.
    
    Set USE_MOCK_DATA = True for testing without API connection
    """

    EASYSHIP_API_URL = "https://sandbox-api.easyship.com/2024-09/rates"
    EASYSHIP_API_KEY = "sand_0Cm94eqHpyshOMLu34B7TIZRUSr4zGOkE3wYZDvSySk="
    
    # ⚠⚠⚠ IMPORTANT: SET THIS TO True FOR TESTING ⚠⚠⚠
    USE_MOCK_DATA = True  # ← MAKE SURE THIS IS True!
    
    REQUEST_TIMEOUT = (10, 30)

    ALLOWED_COURIERS = ["FEDEX", "UPS", "USPS"]
    
    SERVICE_TYPE_MAPPINGS = {
        "FEDEX": {
            "GROUND": ["GROUND", "FEDEX GROUND", "GROUND HOME DELIVERY"],
            "EXPEDITED": ["2DAY", "2-DAY", "FEDEX 2DAY"],
            "OVERNIGHT": ["OVERNIGHT", "FIRST OVERNIGHT", "PRIORITY OVERNIGHT", "STANDARD OVERNIGHT"]
        },
        "UPS": {
            "GROUND": ["GROUND", "UPS GROUND"],
            "EXPEDITED": ["2ND DAY AIR", "2ND DAY AIR AM", "3 DAY SELECT"],
            "OVERNIGHT": ["NEXT DAY AIR", "NEXT DAY AIR SAVER", "NEXT DAY AIR EARLY AM"]
        },
        "USPS": {
            "GROUND": ["GROUND ADVANCE", "PARCEL SELECT GROUND", "MEDIA MAIL", "PRIORITY MAIL"],
            "EXPEDITED": ["PRIORITY MAIL EXPRESS"],
            "OVERNIGHT": ["PRIORITY MAIL EXPRESS 1-DAY"]
        }
    }

    STATE_TAX_RATES = {
        "TX": 0.0825,
        "CA": 0.0725,
        "NY": 0.04,
        "FL": 0.06,
    }

    def get_mock_shipping_data(self):
        """
        Returns mock shipping data for testing when API is unavailable
        """
        return {
            "rates": [
                {
                    "courier_service": {"name": "FedEx"},
                    "service_name": "FedEx Ground",
                    "total_charge": 12.50,
                    "min_delivery_time": 3,
                    "max_delivery_time": 5,
                    "service_type": "GROUND"
                },
                {
                    "courier_service": {"name": "FedEx"},
                    "service_name": "FedEx 2Day",
                    "total_charge": 25.00,
                    "min_delivery_time": 2,
                    "max_delivery_time": 2,
                    "service_type": "EXPEDITED"
                },
                {
                    "courier_service": {"name": "FedEx"},
                    "service_name": "FedEx Priority Overnight",
                    "total_charge": 45.00,
                    "min_delivery_time": 1,
                    "max_delivery_time": 1,
                    "service_type": "OVERNIGHT"
                },
                {
                    "courier_service": {"name": "UPS"},
                    "service_name": "UPS Ground",
                    "total_charge": 11.75,
                    "min_delivery_time": 3,
                    "max_delivery_time": 5,
                    "service_type": "GROUND"
                },
                {
                    "courier_service": {"name": "UPS"},
                    "service_name": "UPS 2nd Day Air",
                    "total_charge": 28.50,
                    "min_delivery_time": 2,
                    "max_delivery_time": 2,
                    "service_type": "EXPEDITED"
                },
                {
                    "courier_service": {"name": "UPS"},
                    "service_name": "UPS Next Day Air",
                    "total_charge": 50.00,
                    "min_delivery_time": 1,
                    "max_delivery_time": 1,
                    "service_type": "OVERNIGHT"
                },
                {
                    "courier_service": {"name": "USPS"},
                    "service_name": "USPS Priority Mail",
                    "total_charge": 8.95,
                    "min_delivery_time": 2,
                    "max_delivery_time": 3,
                    "service_type": "GROUND"
                },
                {
                    "courier_service": {"name": "USPS"},
                    "service_name": "USPS Priority Mail Express",
                    "total_charge": 35.00,
                    "min_delivery_time": 1,
                    "max_delivery_time": 2,
                    "service_type": "EXPEDITED"
                }
            ]
        }

    def has_economic_nexus(self, state):
        return False

    def calculate_tax_rate(self, country, state, account_type="individual", has_resale_cert=False):
        if country.upper() != "US":
            return 0.0, "International shipping - no tax"
        
        state = state.upper()
        
        if account_type.lower() == "individual":
            if state == "TX":
                return self.STATE_TAX_RATES["TX"], "Texas individual sales tax"
            else:
                return 0.0, "Individual account - no tax for out-of-state shipping"
        
        elif account_type.lower() == "enterprise":
            if state == "TX":
                if has_resale_cert:
                    return 0.0, "Texas enterprise with resale certificate - no tax"
                else:
                    return self.STATE_TAX_RATES["TX"], "Texas enterprise without resale certificate"
            else:
                if self.has_economic_nexus(state):
                    if has_resale_cert:
                        return 0.0, f"Economic nexus in {state} with resale certificate - no tax"
                    else:
                        state_rate = self.STATE_TAX_RATES.get(state, 0.0)
                        return state_rate, f"Economic nexus in {state} - applying state tax"
                else:
                    return 0.0, f"No economic nexus in {state} - no tax"
        
        return 0.0, "No tax applicable"

    def categorize_service_type(self, courier_name, service_name):
        courier_name = courier_name.upper()
        service_name = service_name.upper()
        
        for courier_key, service_mappings in self.SERVICE_TYPE_MAPPINGS.items():
            if courier_key in courier_name:
                for service_type, keywords in service_mappings.items():
                    if any(keyword in service_name for keyword in keywords):
                        return service_type
        
        return "GROUND"
    
    def filter_allowed_couriers(self, rates):
        filtered_rates = []
        
        for rate in rates:
            courier_service = rate.get("courier_service", {})
            courier_name = courier_service.get("name", "").upper()
            
            if any(allowed_courier in courier_name for allowed_courier in self.ALLOWED_COURIERS):
                rate["service_type"] = self.categorize_service_type(
                    courier_name, 
                    rate.get("service_name", "")
                )
                filtered_rates.append(rate)
        
        return filtered_rates

    def call_easyship_api(self, payload, headers):
        try:
            response = requests.post(
                self.EASYSHIP_API_URL,
                json=payload,
                headers=headers,
                timeout=self.REQUEST_TIMEOUT
            )
            return response, None
        
        except (ConnectionError, Timeout, RequestException) as e:
            error_msg = f"Network error: {str(e)}"
            logger.error(f"API call failed: {error_msg}")
            return None, error_msg

    def post(self, request):
        # Validate input
        input_serializer = ShippingInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        user_data = input_serializer.validated_data

        # Get warehouse
        warehouse = Warehouse.objects.first()
        if not warehouse:
            return Response(
                {"error": "Warehouse origin is not configured"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Get account settings
        account_type = user_data.get("account_type", "individual")
        has_resale_cert = user_data.get("has_resale_cert", False)

        # Check if using mock data
        if self.USE_MOCK_DATA:
            logger.info("Using mock shipping data for testing")
            data = self.get_mock_shipping_data()
            all_rates = data.get("rates", [])
        else:
            # Build Easyship payload
            payload = {
                "origin_address": {
                    "country_alpha2": warehouse.country_alpha2,
                    "state": warehouse.state,
                    "city": warehouse.city,
                    "postal_code": warehouse.postal_code
                },
                "destination_address": {
                    "country_alpha2": user_data["country"],
                    "state": user_data["state"],
                    "city": user_data["city"],
                    "postal_code": user_data["postal_code"]
                },
                "incoterms": "DDU",
                "insurance": {"is_insured": False},
                "courier_settings": {
                    "show_courier_logo_url": False,
                    "apply_shipping_rules": True
                },
                "shipping_settings": {
                    "units": {"weight": "kg", "dimensions": "cm"}
                },
                "parcels": [
                    {
                        "items": [
                            {
                                "actual_weight": 1.2,
                                "quantity": 1,
                                "declared_currency": "USD",
                                "declared_customs_value": 100,
                                "origin_country_alpha2": warehouse.country_alpha2,
                                "category": "Toys",
                                "hs_code": "95030039",
                                "dimensions": {"length": 20, "width": 10, "height": 5},
                                "contains_battery_pi966": False,
                                "contains_battery_pi967": False,
                                "contains_liquids": False,
                            }
                        ]
                    }
                ]
            }

            headers = {
                "Authorization": f"Bearer {self.EASYSHIP_API_KEY}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }

            # Call API
            api_response, error_msg = self.call_easyship_api(payload, headers)
            
            if error_msg:
                return Response(
                    {
                        "error": "Failed to fetch shipping rates",
                        "details": error_msg,
                        "suggestion": "Set USE_MOCK_DATA = True in views.py for testing"
                    }, 
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )

            if api_response.status_code != 200:
                try:
                    error_details = api_response.json()
                except:
                    error_details = api_response.text
                
                return Response(
                    {
                        "error": "Easyship API request failed",
                        "status_code": api_response.status_code,
                        "details": error_details
                    }, 
                    status=api_response.status_code
                )

            try:
                data = api_response.json()
            except ValueError:
                return Response(
                    {"error": "Invalid JSON response from Easyship API"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            all_rates = data.get("rates", [])

        if not all_rates:
            return Response(
                {"error": "No shipping rates available"}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # Filter rates
        filtered_rates = self.filter_allowed_couriers(all_rates)

        if not filtered_rates:
            return Response(
                {"error": "No FedEx, UPS, or USPS shipping rates available"}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # Get cheapest rate
        cheapest_rate = min(filtered_rates, key=lambda r: r.get("total_charge", float('inf')))
        shipping_rate = cheapest_rate.get("total_charge", 0)

        # Calculate tax
        tax_rate, tax_reason = self.calculate_tax_rate(
            user_data["country"], 
            user_data["state"], 
            account_type, 
            has_resale_cert
        )
        estimated_tax = round(shipping_rate * tax_rate, 2)

        # Save request
        try:
            shipping_record = ShippingRequest.objects.create(
                user_address=user_data,
                shipping_rate=shipping_rate,
                tax=estimated_tax,
                response_data={"rates": filtered_rates, "mock": self.USE_MOCK_DATA},
            )
        except Exception as e:
            logger.error(f"Failed to save shipping record: {str(e)}")
            shipping_record = None

        # Build response
        response_payload = {
            "success": True,
            "mock_mode": self.USE_MOCK_DATA,
            "shipping_rate": shipping_rate,
            "tax": estimated_tax,
            "tax_rate": f"{tax_rate * 100:.2f}%",
            "tax_reason": tax_reason,
            "total_cost": round(shipping_rate + estimated_tax, 2),
            "account_type": account_type,
            "courier_name": cheapest_rate.get("courier_service", {}).get("name", "Unknown"),
            "service_name": cheapest_rate.get("service_name", "Standard"),
            "service_type": cheapest_rate.get("service_type", "GROUND"),
            "estimated_delivery": f"{cheapest_rate.get('min_delivery_time', 'N/A')}-{cheapest_rate.get('max_delivery_time', 'N/A')} days",
            "shipping_request_id": shipping_record.id if shipping_record else None,
            "available_services": [
                {
                    "courier_name": rate.get("courier_service", {}).get("name", "Unknown"),
                    "service_name": rate.get("service_name", "Standard"),
                    "service_type": rate.get("service_type", "GROUND"),
                    "total_charge": rate.get("total_charge", 0),
                    "delivery_time": f"{rate.get('min_delivery_time', 'N/A')}-{rate.get('max_delivery_time', 'N/A')} days",
                    "with_tax": round(rate.get("total_charge", 0) + (rate.get("total_charge", 0) * tax_rate), 2)
                }
                for rate in filtered_rates
            ]
        }

        return Response(response_payload, status=status.HTTP_200_OK)


class SaveShippingAPIView(APIView):
    def post(self, request):
        serializer = ShippingRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'status': 'success', 'message': 'Shipping info saved'}, 
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ShippingRequestListAPIView(ListAPIView):
    queryset = ShippingRequest.objects.all().order_by('-created_at')
    serializer_class = ShippingRequestSerializer


class WarehouseListAPIView(ListAPIView):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer