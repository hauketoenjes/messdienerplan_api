from django.urls import path, include

from . import views
from rest_framework_nested import routers

router = routers.DefaultRouter()

router.register(r'locations', views.LocationView)
router.register(r'roles', views.RoleView)
router.register(r'acolytes', views.AcolyteView)
router.register(r'groups', views.GroupView)
router.register(r'types', views.TypeView, basename='types')
router.register(r'plans', views.PlanView, basename='plans')
router.register(r'current', views.CurrentPlanView, basename='current')

masses_router = routers.NestedDefaultRouter(router, r'plans', lookup='plan')
masses_router.register(r'masses', views.MassView, basename='masses')

mass_acolyte_router = routers.NestedDefaultRouter(masses_router, r'masses', lookup='mass')
mass_acolyte_router.register(r'acolytes', views.MassAcolyteView, basename='mass-acolytes')

requirements_router = routers.NestedDefaultRouter(router, r'types', lookup='type')
requirements_router.register(r'requirements', views.RequirementView, basename='requirements')

rules_router = routers.NestedDefaultRouter(router, r'types', lookup='type')
rules_router.register(r'rules', views.RuleView, basename='type-rules')

classifications_router = routers.NestedDefaultRouter(router, r'groups', lookup='group')
classifications_router.register(r'classifications', views.ClassificationView, basename='group-classifications')

acolyte_mass_router = routers.NestedDefaultRouter(router, r'acolytes', lookup='acolyte')
acolyte_mass_router.register(r'masses', views.AcolyteMassView, basename='acolyte-masses')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(masses_router.urls)),
    path('', include(requirements_router.urls)),
    path('', include(rules_router.urls)),
    path('', include(classifications_router.urls)),
    path('', include(mass_acolyte_router.urls)),
    path('', include(acolyte_mass_router.urls)),
]
