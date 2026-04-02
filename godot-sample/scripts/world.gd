extends Node2D

const TILE_SIZE := 16
const WORLD_W := 50
const WORLD_H := 40


func _ready() -> void:
	_generate_terrain()
	_place_objects()
	_place_effects()
	_place_weapons()
	_place_buildings()
	_place_items()
	_place_npcs()


# ============================================================
# TERRAIN
# ============================================================

func _generate_terrain() -> void:
	var grass_tex := load("res://assets/terrain/grass.png") as Texture2D
	var dirt_tex := load("res://assets/terrain/dirt.png") as Texture2D
	var stone_tex := load("res://assets/terrain/stone.png") as Texture2D
	var sand_tex := load("res://assets/terrain/sand.png") as Texture2D

	if grass_tex == null:
		return

	var tiles := [grass_tex, grass_tex, grass_tex, grass_tex,
				  dirt_tex, stone_tex, sand_tex]

	for y in WORLD_H:
		for x in WORLD_W:
			var s := Sprite2D.new()
			var idx := 0
			var noise_val := sin(x * 0.7 + y * 0.5) * cos(x * 0.3 - y * 0.8)
			if noise_val > 0.6:
				idx = 4  # dirt
			elif noise_val > 0.75:
				idx = 5  # stone
			elif noise_val < -0.7:
				idx = 6  # sand

			# Stone floor for castle courtyard (top-right)
			if x >= 33 and x <= 46 and y >= 1 and y <= 12:
				idx = 5

			# Dirt paths between buildings (village row)
			if y >= 19 and y <= 20 and x >= 1 and x <= 30:
				idx = 4
			if y >= 26 and y <= 27 and x >= 3 and x <= 28:
				idx = 4

			# Sand beach near water
			if y >= 10 and y <= 14 and x >= 11 and x <= 16:
				idx = 6

			s.texture = tiles[idx]
			s.position = Vector2(x * TILE_SIZE, y * TILE_SIZE)
			s.centered = false
			s.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
			$Terrain.add_child(s)

	# Water pond
	for wy in range(4):
		for wx in range(5):
			var obj := _create_animated_sprite(
				"res://assets/objects/water_waves.png", 8, 8.3, Vector2i(16, 16))
			obj.position = Vector2((12 + wx) * TILE_SIZE, (11 + wy) * TILE_SIZE)
			obj.centered = false
			$Objects.add_child(obj)

	# Lava pool near dungeon
	var lava_tex_path := "res://assets/terrain/lava.png"
	if ResourceLoader.exists(lava_tex_path):
		for ly in range(2):
			for lx in range(3):
				var lava := _create_animated_sprite(
					lava_tex_path, 8, 6.7, Vector2i(16, 16))
				lava.position = Vector2((41 + lx) * TILE_SIZE, (26 + ly) * TILE_SIZE)
				lava.centered = false
				$Objects.add_child(lava)


# ============================================================
# NATURAL OBJECTS
# ============================================================

func _place_objects() -> void:
	# Forest trees (scattered)
	var tree_positions := [
		Vector2(3, 2), Vector2(7, 1), Vector2(15, 3), Vector2(1, 5),
		Vector2(2, 10), Vector2(17, 14), Vector2(10, 5), Vector2(0, 15),
		Vector2(5, 16), Vector2(8, 17), Vector2(3, 35), Vector2(7, 36),
		Vector2(15, 35), Vector2(28, 3), Vector2(30, 6), Vector2(25, 12),
	]
	for pos in tree_positions:
		var tree := _create_animated_sprite(
			"res://assets/objects/tree_sway.png", 8, 6.7, Vector2i(16, 16))
		tree.position = pos * TILE_SIZE
		tree.centered = false
		tree.scale = Vector2(2, 2)
		$Objects.add_child(tree)

	# Grass patches
	var grass_positions := [
		Vector2(5, 4), Vector2(8, 7), Vector2(13, 2), Vector2(1, 6),
		Vector2(18, 14), Vector2(6, 15), Vector2(22, 8), Vector2(28, 14),
		Vector2(4, 25), Vector2(10, 30), Vector2(20, 35), Vector2(30, 30),
	]
	for pos in grass_positions:
		var g := _create_animated_sprite(
			"res://assets/objects/grass_sway.png", 8, 8.3, Vector2i(16, 16))
		g.position = pos * TILE_SIZE
		g.centered = false
		$Objects.add_child(g)

	# Rocks
	var rock_positions := [
		Vector2(9, 3), Vector2(4, 8), Vector2(20, 10), Vector2(30, 15),
		Vector2(14, 30), Vector2(38, 30),
	]
	for rpos in rock_positions:
		var rock := _create_animated_sprite(
			"res://assets/objects/rock_idle.png", 8, 5.0, Vector2i(16, 16))
		rock.position = rpos * TILE_SIZE
		rock.centered = false
		rock.scale = Vector2(1.5, 1.5)
		$Objects.add_child(rock)

	# Leaf swirls
	for lpos in [Vector2(11, 10), Vector2(6, 36), Vector2(28, 8)]:
		var leaves := _create_animated_sprite(
			"res://assets/objects/leaf_swirl.png", 8, 10.0, Vector2i(16, 16))
		leaves.position = lpos * TILE_SIZE
		leaves.centered = false
		$Objects.add_child(leaves)

	# Sky cycle background
	var sky := _create_animated_sprite(
		"res://assets/objects/sky_cycle.png", 8, 3.3, Vector2i(16, 16))
	sky.position = Vector2(0, -20)
	sky.centered = false
	sky.scale = Vector2(50, 1.5)
	$Background.add_child(sky)

	# Clouds scrolling
	for ci in range(4):
		var cloud := _create_animated_sprite(
			"res://assets/objects/sky_clouds.png", 8, 4.0, Vector2i(32, 16))
		cloud.position = Vector2(ci * 200, -10)
		cloud.centered = false
		cloud.scale = Vector2(2, 1.5)
		cloud.modulate.a = 0.7
		$Background.add_child(cloud)


# ============================================================
# EFFECTS
# ============================================================

func _place_effects() -> void:
	# Campfire with fire
	var fire := _create_animated_sprite(
		"res://assets/effects/fire.png", 8, 10.0, Vector2i(16, 16))
	fire.position = Vector2(6, 6) * TILE_SIZE
	fire.centered = false
	fire.scale = Vector2(1.5, 1.5)
	$Effects.add_child(fire)

	# Smoke above campfire
	var smoke := _create_animated_sprite(
		"res://assets/effects/smoke_puff.png", 6, 8.0, Vector2i(16, 16))
	smoke.position = Vector2(6, 5) * TILE_SIZE
	smoke.centered = false
	smoke.modulate.a = 0.6
	$Effects.add_child(smoke)

	# Magic sparkle near water
	var sparkle := _create_animated_sprite(
		"res://assets/effects/magic_sparkle.png", 8, 12.5, Vector2i(16, 16))
	sparkle.position = Vector2(11, 12) * TILE_SIZE
	sparkle.centered = false
	$Effects.add_child(sparkle)

	# Heal aura near a tree
	var heal := _create_animated_sprite(
		"res://assets/effects/heal_aura.png", 8, 10.0, Vector2i(16, 16))
	heal.position = Vector2(10, 5) * TILE_SIZE
	heal.centered = false
	heal.scale = Vector2(1.5, 1.5)
	$Effects.add_child(heal)

	# Portal at adventure zone
	var portal := _create_animated_sprite(
		"res://assets/effects/portal.png", 8, 11.1, Vector2i(16, 16))
	portal.position = Vector2(44, 35) * TILE_SIZE
	portal.centered = false
	portal.scale = Vector2(2, 2)
	$Effects.add_child(portal)

	# Lightning near wizard tower
	var lightning := _create_animated_sprite(
		"res://assets/effects/lightning_strike.png", 6, 10.0, Vector2i(16, 16))
	lightning.position = Vector2(43, 6) * TILE_SIZE
	lightning.centered = false
	lightning.scale = Vector2(2, 2)
	$Effects.add_child(lightning)

	# Energy orb near crystal cave
	var orb := _create_animated_sprite(
		"res://assets/effects/energy_orb.png", 8, 10.0, Vector2i(16, 16))
	orb.position = Vector2(42, 31) * TILE_SIZE
	orb.centered = false
	$Effects.add_child(orb)

	# Shield bash effect near castle gate
	var shield_bash := _create_animated_sprite(
		"res://assets/effects/shield_bash.png", 6, 12.0, Vector2i(16, 16))
	shield_bash.position = Vector2(36, 4) * TILE_SIZE
	shield_bash.centered = false
	$Effects.add_child(shield_bash)

	# Frost burst near ice area
	var frost := _create_animated_sprite(
		"res://assets/effects/frost_burst.png", 6, 10.0, Vector2i(16, 16))
	frost.position = Vector2(46, 12) * TILE_SIZE
	frost.centered = false
	$Effects.add_child(frost)


# ============================================================
# WEAPONS (display + scattered enchanted)
# ============================================================

func _place_weapons() -> void:
	# Weapon rack inside castle courtyard
	var rack_weapons := [
		"weapon_sword", "weapon_axe", "weapon_mace", "weapon_spear",
		"weapon_dagger", "weapon_hammer", "weapon_scythe",
	]
	for i: int in rack_weapons.size():
		var wname: String = rack_weapons[i]
		var tex_path: String = "res://assets/weapons/" + wname + ".png"
		if not ResourceLoader.exists(tex_path):
			continue
		var s := Sprite2D.new()
		s.texture = load(tex_path)
		s.position = Vector2((34 + i) * TILE_SIZE, 3 * TILE_SIZE)
		s.centered = false
		s.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		s.scale = Vector2(2, 2)
		$Weapons.add_child(s)

	# Ranged weapons rack
	var ranged := ["weapon_bow", "weapon_crossbow", "weapon_wand", "weapon_staff"]
	for i: int in ranged.size():
		var rname: String = ranged[i]
		var tex_path: String = "res://assets/weapons/" + rname + ".png"
		if not ResourceLoader.exists(tex_path):
			continue
		var s := Sprite2D.new()
		s.texture = load(tex_path)
		s.position = Vector2((34 + i) * TILE_SIZE, 6 * TILE_SIZE)
		s.centered = false
		s.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		s.scale = Vector2(2, 2)
		$Weapons.add_child(s)

	# Shields display
	var shields := ["weapon_round_shield", "weapon_kite_shield", "weapon_tower_shield"]
	for i: int in shields.size():
		var sname: String = shields[i]
		var tex_path: String = "res://assets/weapons/" + sname + ".png"
		if not ResourceLoader.exists(tex_path):
			continue
		var s := Sprite2D.new()
		s.texture = load(tex_path)
		s.position = Vector2((39 + i) * TILE_SIZE, 6 * TILE_SIZE)
		s.centered = false
		s.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		s.scale = Vector2(2, 2)
		$Weapons.add_child(s)

	# Legendary items in castle throne area
	for rarity in ["weapon_legendary_sword", "weapon_epic_staff"]:
		var tex_path: String = "res://assets/weapons/" + rarity + ".png"
		if not ResourceLoader.exists(tex_path):
			continue
		var s := Sprite2D.new()
		s.texture = load(tex_path)
		s.position = Vector2(38 * TILE_SIZE, 9 * TILE_SIZE)
		s.centered = false
		s.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		s.scale = Vector2(3, 3)
		$Weapons.add_child(s)

	# Enchanted weapons scattered in the world
	var enchanted := [
		{"file": "weapon_fire_sword", "pos": Vector2(7, 6), "fps": 10.0},
		{"file": "weapon_ice_sword", "pos": Vector2(13, 10), "fps": 8.3},
		{"file": "weapon_lightning_axe", "pos": Vector2(4, 4), "fps": 12.5},
		{"file": "weapon_poison_dagger", "pos": Vector2(1, 14), "fps": 8.3},
		{"file": "weapon_shuriken_spin", "pos": Vector2(16, 8), "fps": 16.7},
		{"file": "weapon_orb_pulse", "pos": Vector2(12, 13), "fps": 8.3},
		{"file": "weapon_staff_charge", "pos": Vector2(9, 5), "fps": 10.0},
	]
	for e: Dictionary in enchanted:
		var ew := _create_animated_sprite(
			"res://assets/weapons/" + e["file"] + ".png", 8, e["fps"], Vector2i(16, 16))
		ew.position = e["pos"] * TILE_SIZE
		ew.centered = false
		ew.scale = Vector2(1.5, 1.5)
		$Weapons.add_child(ew)


# ============================================================
# BUILDINGS (Village + Castle + Adventure)
# ============================================================

func _place_buildings() -> void:
	var BSCALE := Vector2(4, 4)
	var BIG := Vector2(6, 6)
	var SMALL := Vector2(3, 3)

	# === Village Row ===
	var house := _create_building_animated(
		"res://assets/buildings/house_idle.png", 8, 5.0, BSCALE)
	house.position = Vector2(2, 20) * TILE_SIZE
	$Buildings.add_child(house)

	var brick_house := _create_building_static(
		"res://assets/buildings/house_brick.png", BSCALE)
	brick_house.position = Vector2(7, 20) * TILE_SIZE
	$Buildings.add_child(brick_house)

	var wood_house := _create_building_static(
		"res://assets/buildings/house_wood.png", BSCALE)
	wood_house.position = Vector2(12, 20) * TILE_SIZE
	$Buildings.add_child(wood_house)

	var inn := _create_building_animated(
		"res://assets/buildings/inn_idle.png", 8, 6.7, BSCALE)
	inn.position = Vector2(17, 20) * TILE_SIZE
	$Buildings.add_child(inn)

	var shop := _create_building_animated(
		"res://assets/buildings/shop_idle.png", 8, 6.7, BSCALE)
	shop.position = Vector2(22, 20) * TILE_SIZE
	$Buildings.add_child(shop)

	var smith := _create_building_animated(
		"res://assets/buildings/blacksmith_idle.png", 8, 8.3, BSCALE)
	smith.position = Vector2(27, 20) * TILE_SIZE
	$Buildings.add_child(smith)

	# === Town Center ===
	var church := _create_building_static(
		"res://assets/buildings/church.png", BIG)
	church.position = Vector2(18, 27) * TILE_SIZE
	$Buildings.add_child(church)

	var fountain := _create_building_animated(
		"res://assets/buildings/fountain_splash.png", 8, 8.3, BSCALE)
	fountain.position = Vector2(12, 28) * TILE_SIZE
	$Buildings.add_child(fountain)

	var well := _create_building_animated(
		"res://assets/buildings/well_idle.png", 8, 5.0, SMALL)
	well.position = Vector2(8, 29) * TILE_SIZE
	$Buildings.add_child(well)

	var market := _create_building_static(
		"res://assets/buildings/market_stall.png", SMALL)
	market.position = Vector2(4, 28) * TILE_SIZE
	$Buildings.add_child(market)

	# === Outskirts ===
	var barn := _create_building_static(
		"res://assets/buildings/barn.png", BSCALE)
	barn.position = Vector2(2, 34) * TILE_SIZE
	$Buildings.add_child(barn)

	var windmill := _create_building_animated(
		"res://assets/buildings/windmill_spin.png", 8, 6.7, BIG)
	windmill.position = Vector2(9, 33) * TILE_SIZE
	$Buildings.add_child(windmill)

	var tent := _create_building_static(
		"res://assets/buildings/tent.png", SMALL)
	tent.position = Vector2(26, 28) * TILE_SIZE
	$Buildings.add_child(tent)

	# === Castle Area ===
	var castle := _create_building_animated(
		"res://assets/buildings/castle_idle.png", 8, 6.7, BIG)
	castle.position = Vector2(35, 1) * TILE_SIZE
	$Buildings.add_child(castle)

	var watchtower := _create_building_animated(
		"res://assets/buildings/watchtower_idle.png", 8, 7.1, BIG)
	watchtower.position = Vector2(32, 10) * TILE_SIZE
	$Buildings.add_child(watchtower)

	var wizard := _create_building_animated(
		"res://assets/buildings/tower_idle.png", 8, 5.6, BIG)
	wizard.position = Vector2(42, 8) * TILE_SIZE
	$Buildings.add_child(wizard)

	# === Adventure Locations ===
	var dungeon := _create_building_animated(
		"res://assets/buildings/dungeon_entrance_idle.png", 8, 7.7, BSCALE)
	dungeon.position = Vector2(40, 25) * TILE_SIZE
	$Buildings.add_child(dungeon)

	var cave := _create_building_animated(
		"res://assets/buildings/crystal_cave_idle.png", 8, 6.3, BSCALE)
	cave.position = Vector2(40, 32) * TILE_SIZE
	$Buildings.add_child(cave)

	var lighthouse := _create_building_animated(
		"res://assets/buildings/lighthouse_idle.png", 8, 6.7, BIG)
	lighthouse.position = Vector2(46, 18) * TILE_SIZE
	$Buildings.add_child(lighthouse)

	var bridge := _create_building_static(
		"res://assets/buildings/bridge.png", BSCALE)
	bridge.position = Vector2(20, 15) * TILE_SIZE
	$Buildings.add_child(bridge)

	var ruins := _create_building_static(
		"res://assets/buildings/ruins.png", BIG)
	ruins.position = Vector2(35, 18) * TILE_SIZE
	$Buildings.add_child(ruins)


# ============================================================
# ITEMS (scattered pickups)
# ============================================================

func _place_items() -> void:
	# Items near buildings and paths
	var item_placements := [
		{"file": "items/potions/health_potion.png", "pos": Vector2(8, 22)},
		{"file": "items/potions/mana_potion.png", "pos": Vector2(13, 22)},
		{"file": "items/potions/stamina_potion.png", "pos": Vector2(18, 22)},
		{"file": "items/gems/ruby.png", "pos": Vector2(36, 10)},
		{"file": "items/gems/sapphire.png", "pos": Vector2(38, 10)},
		{"file": "items/gems/emerald.png", "pos": Vector2(40, 10)},
		{"file": "items/misc/coin.png", "pos": Vector2(5, 28)},
		{"file": "items/misc/coin.png", "pos": Vector2(6, 28)},
		{"file": "items/misc/coin.png", "pos": Vector2(7, 29)},
		{"file": "items/misc/key.png", "pos": Vector2(39, 25)},
		{"file": "items/misc/chest.png", "pos": Vector2(41, 33)},
		{"file": "items/misc/chest.png", "pos": Vector2(37, 5)},
		{"file": "items/weapons/sword.png", "pos": Vector2(3, 6)},
		{"file": "items/weapons/shield.png", "pos": Vector2(4, 6)},
	]

	for item: Dictionary in item_placements:
		var tex_path: String = "res://assets/" + item["file"]
		if not ResourceLoader.exists(tex_path):
			continue
		var s := Sprite2D.new()
		s.texture = load(tex_path)
		s.position = item["pos"] * TILE_SIZE
		s.centered = false
		s.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		s.scale = Vector2(2, 2)
		$Items.add_child(s)


# ============================================================
# NPCs (villagers near buildings, merchant at market)
# ============================================================

func _place_npcs() -> void:
	# Villagers wandering near buildings
	var villager_positions := [
		Vector2(5, 22), Vector2(10, 22), Vector2(15, 27),
		Vector2(20, 27), Vector2(25, 22),
	]
	for pos in villager_positions:
		var villager := _create_animated_sprite(
			"res://assets/characters/npcs/villager.png", 8, 6.7, Vector2i(16, 16))
		villager.position = pos * TILE_SIZE
		villager.centered = false
		villager.scale = Vector2(2, 2)
		$NPCs.add_child(villager)

	# Merchant at market stall
	var merchant := _create_animated_sprite(
		"res://assets/characters/npcs/merchant.png", 8, 5.0, Vector2i(16, 16))
	merchant.position = Vector2(5, 29) * TILE_SIZE
	merchant.centered = false
	merchant.scale = Vector2(2, 2)
	$NPCs.add_child(merchant)


# ============================================================
# HELPERS
# ============================================================

func _create_building_animated(tex_path: String, frame_count: int,
		fps: float, bscale: Vector2) -> AnimatedSprite2D:
	var sprite := _create_animated_sprite(tex_path, frame_count, fps, Vector2i(16, 16))
	sprite.scale = bscale
	sprite.centered = false
	return sprite


func _create_building_static(tex_path: String, bscale: Vector2) -> Sprite2D:
	var s := _create_static_sprite(tex_path)
	s.scale = bscale
	return s


func _create_static_sprite(tex_path: String) -> Sprite2D:
	var s := Sprite2D.new()
	s.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	if ResourceLoader.exists(tex_path):
		s.texture = load(tex_path)
	s.centered = false
	return s


func _create_animated_sprite(tex_path: String, frame_count: int,
		fps: float, frame_size: Vector2i) -> AnimatedSprite2D:
	var sprite := AnimatedSprite2D.new()
	sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST

	if not ResourceLoader.exists(tex_path):
		return sprite

	var frames := SpriteFrames.new()
	if frames.has_animation("default"):
		frames.remove_animation("default")

	frames.add_animation("default")
	frames.set_animation_speed("default", fps)
	frames.set_animation_loop("default", true)

	var sheet: Texture2D = load(tex_path)
	for i in frame_count:
		var atlas := AtlasTexture.new()
		atlas.atlas = sheet
		atlas.region = Rect2(i * frame_size.x, 0, frame_size.x, frame_size.y)
		frames.add_frame("default", atlas)

	sprite.sprite_frames = frames
	sprite.play("default")
	return sprite
