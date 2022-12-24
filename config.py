BOT_API_TOKEN = '5959178305:AAFg79o6AuVo4Y3RZylNcoF9LLjBVpjTdeI'
WEATHER_API_KEY = 'f8c325703dfb5eef357ce83cd980c924'

ADMIN_ID = 800903277

CURRENT_WEATHER_API_CALL = (
        'https://api.openweathermap.org/data/2.5/weather?'
        'lat={latitude}&lon={longitude}&'
        'appid=' + WEATHER_API_KEY + '&units=metric' + '&lang=ru'
)
