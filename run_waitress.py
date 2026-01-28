from waitress import serve
from ong_sol.wsgi import application

serve(application, host="0.0.0.0", port=80)
