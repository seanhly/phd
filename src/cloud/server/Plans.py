from cloud.server.Plan import Plan
from cloud.vendors.Vultr import Vultr


def lowest_cost(plan: Plan):
	return plan.monthly_cost


class Plans:
	@classmethod
	def cheapest_plan(cls, **kwargs):
		return Vultr.list_plans(sort_by=lowest_cost, **kwargs)[0]
