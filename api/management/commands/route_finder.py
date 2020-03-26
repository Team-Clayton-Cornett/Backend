import route_visualization.get_routes as routes
from django.core.management.base import BaseCommand, CommandError


# The purpose of this command is to generate a route for three different groups
# Using openrouteservice API and ortools, get the best route to visit
# each parking location in every group, and plot onto a map

# OUTPUT: capstone/route_visualization
#         three_route_enforcement.html = the visualization for an optimal route each group could take
#         CondensedRoutes = a collection of .json files that represent the optimal route by parking name and duration
#         FullRoutes = full route info with directions returned by the openrouteservice API
 
class Command(BaseCommand):
    help = '*Create Help Text*'

    def handle(self, *args, **options):
        routes.start()
       
