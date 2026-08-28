"""Constants for the sitSolar integration."""

DOMAIN = "sitsolar"
DEFAULT_NAME = "sitSolar"
DEFAULT_BASE_URL = "https://enjoysolar.si-neng.com"
DEFAULT_API_PREFIX = "/prod-api"
DEFAULT_SCAN_INTERVAL = 30

CONF_STATION_CODE = "station_code"

PLATFORMS = ["sensor"]

# API Endpoints
ENDPOINT_LOGIN = "/auth/login"
ENDPOINT_LOGOUT = "/auth/logout"
ENDPOINT_AUTH_INFO = "/auth/info"
ENDPOINT_AES_KEY = "/auth/aesKey"
ENDPOINT_STATION_LIST = "/dev/info/app/v1/station/info/appPageStationBusinessNew"
ENDPOINT_STATION_DETAIL = "/dev/info/app/v1/station/info/appGetStationDetailV2"
ENDPOINT_STATION_OVERVIEW = "/business/app/v1/total/overview/appStationOverviewData"
ENDPOINT_SINGLE_STATION_OVERVIEW = "/business/app/v1/single/overview/appSingleStationOverviewData"
ENDPOINT_ENERGY_FLOW = "/business/single/overview/stationEnergyFlowDiagram"
ENDPOINT_ENERGY_FLOW_REALTIME = "/business/single/overview/stationEnergyFlowDiagramReTime"
ENDPOINT_STORAGE_INVERTER_LIST = "/dev/info/app/v1/devmonitor/appPageStoredInverterMoniterList"
ENDPOINT_DEVICE_REALTIME = "/dev/info/app/v1/devmonitor/appMonitorRelTime"

# Error codes
ERROR_TOKEN_EXPIRED = {50008, 50012, 50014, 50016}
ERROR_SUCCESS = 20000
