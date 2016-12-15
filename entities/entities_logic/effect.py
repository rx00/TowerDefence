class Effect:
    def __init__(self, owner, caller_link, effect_id, durability, strength):
        self.owner = owner
        self.caller = caller_link
        self.effect_id = effect_id
        self.effect_name = effect_id
        self.effect_strength = strength + 1
        self.effect_durability = durability
        self.effect_method_link = self.available_effects[effect_id]
        self.on_effect_remove_event = {}

    @property
    def available_effects(self):
        return {
            "HealInstantly": self.heal_instantly,
            "Regeneration": self.regeneration,
            "Poison": self.poison,
            "InstantDamage": self.instant_damage,
            "Slowness": self.slowness,
            "Swiftness": self.swiftness
        }

    def swiftness(self):
        self.owner.speed += 2

    def heal_instantly(self):
        self.effect_durability = 0
        self.owner.heal(20 * self.effect_strength)

    def regeneration(self):
        self.owner.heal(5 * self.effect_strength)

    def poison(self):
        self.owner.health_points = max(
            1,
            self.owner.health_points - self.effect_strength
        )

    def instant_damage(self):
        self.owner.health_points -= 20 * self.effect_strength

    def slowness(self):
        self.owner.speed = max(1, self.owner.speed // self.effect_strength)

    def tick(self):
        self.effect_durability -= 1
        if self.effect_durability < 1:
            self.owner.effect_objects.remove(self)
        else:
            try:
                self.effect_method_link()
            except KeyError:
                self.owner.effect_objects.remove(self)

    def on_effect_remove(self):
        for event in self.on_effect_remove_event.values():
            event()
