class Effect:
    def __init__(self, owner, caller_link, effect_id, durability, strength):
        self.owner = owner
        self.caller = caller_link
        self.effect_id = effect_id
        self.effect_name = self.available_effects[effect_id][0]
        self.effect_strength = strength + 1
        self.effect_durability = durability
        self.effect_method_link = self.available_effects[effect_id][1]

    @property
    def available_effects(self):
        return [
            ("HealInstantly", self.heal_instantly),
            ("Regeneration", self.regeneration),
            ("Poison", self.poison),
            ("InstantDamage", self.instant_damage),
            ("Fire", self.fire),
            ("FireResistance", self.fire_resistance),
            ("Swiftness", self.swiftness),
            ("Slowness", self.slowness),
            ("BloodMagic", self.blood_magic)
        ]

    def heal_instantly(self):
        self.effect_durability = 1
        self.owner.heal(20 * self.effect_strength)

    def regeneration(self):
        self.owner.heal(1 * self.effect_strength)

    def poison(self):
        self.owner.health_points -= 1 * self.effect_strength

    def instant_damage(self):
        self.owner.health_points -= 20 * self.effect_strength

    def fire(self):
        self.owner.health_points -= 1 * self.effect_strength

    def fire_resistance(self):
        pass

    def swiftness(self):
        pass

    def slowness(self):
        pass

    def blood_magic(self):
        self.owner.health_points -= 1
        self.caller.heal(0.5 * self.effect_strength)

    def tick(self):
        self.effect_durability -= 1
        if not self.effect_durability or\
                not self.caller.health_points <= 0 or\
                not self.owner.health_points <= 0:
            self.owner.effect_objects.remove(self)
        self.effect_method_link()
