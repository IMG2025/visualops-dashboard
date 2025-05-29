from coreidentity_agents.sentinel import Sentinel

sentinel = Sentinel("coreidentity_agents/sentinel_policy.json")

action = sentinel.intercept("Echo", "data_access", {
    "data_class": "PHI",
    "encryption": False
})

print("Final action decision:", action)
