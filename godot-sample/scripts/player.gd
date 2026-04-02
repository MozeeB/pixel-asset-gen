extends CharacterBody2D

const SPEED := 120.0
const RUN_SPEED := 200.0
const ATTACK_DURATION := 0.53

var current_direction := "down"
var is_attacking := false
var attack_timer := 0.0
var current_weapon_idx := 0

var weapons := [
	{"name": "sword", "slash_file": "weapon_sword_slash", "frames": 6, "fps": 12.0},
	{"name": "axe", "slash_file": "weapon_axe_chop", "frames": 6, "fps": 12.0},
	{"name": "mace", "slash_file": "weapon_mace_swing", "frames": 6, "fps": 12.0},
	{"name": "spear", "slash_file": "weapon_spear_thrust", "frames": 6, "fps": 12.0},
	{"name": "dagger", "slash_file": "weapon_dagger_stab", "frames": 6, "fps": 15.0},
	{"name": "fire_sword", "slash_file": "weapon_fire_sword", "frames": 8, "fps": 10.0},
	{"name": "bow", "slash_file": "weapon_bow_shoot", "frames": 6, "fps": 10.0},
]

@onready var sprite: AnimatedSprite2D = $AnimatedSprite2D
@onready var weapon_sprite: AnimatedSprite2D = $WeaponSprite
@onready var held_weapon: Sprite2D = $HeldWeapon
@onready var camera: Camera2D = $Camera2D
@onready var weapon_label: Label = $WeaponLabel


func _ready() -> void:
	_setup_animations()
	_setup_weapon_animations()
	sprite.play("idle_down")
	_equip_weapon(0)


func _physics_process(delta: float) -> void:
	if is_attacking:
		attack_timer -= delta
		if attack_timer <= 0:
			is_attacking = false
			weapon_sprite.visible = false
			held_weapon.visible = true
		velocity = Vector2.ZERO
		move_and_slide()
		return

	var input := Vector2.ZERO
	input.x = Input.get_axis("ui_left", "ui_right")
	input.y = Input.get_axis("ui_up", "ui_down")

	if input != Vector2.ZERO:
		input = input.normalized()
		_update_direction(input)

	var is_running := Input.is_action_pressed("run")
	var speed := RUN_SPEED if is_running else SPEED
	velocity = input * speed

	if Input.is_action_just_pressed("next_weapon"):
		_equip_weapon((current_weapon_idx + 1) % weapons.size())
	elif Input.is_action_just_pressed("prev_weapon"):
		_equip_weapon((current_weapon_idx - 1 + weapons.size()) % weapons.size())

	if Input.is_action_just_pressed("attack"):
		_attack()
	elif input != Vector2.ZERO:
		var anim_prefix := "run_" if is_running else "walk_"
		sprite.play(anim_prefix + current_direction)
	else:
		sprite.play("idle_" + current_direction)

	move_and_slide()


func _update_direction(input: Vector2) -> void:
	if abs(input.x) > abs(input.y):
		current_direction = "right" if input.x > 0 else "left"
	else:
		current_direction = "down" if input.y > 0 else "up"


func _attack() -> void:
	is_attacking = true
	attack_timer = ATTACK_DURATION
	sprite.play("attack_" + current_direction)

	# Hide held weapon, show slash animation
	held_weapon.visible = false
	var weapon: Dictionary = weapons[current_weapon_idx]
	var anim_name: String = weapon["slash_file"]
	if weapon_sprite.sprite_frames and weapon_sprite.sprite_frames.has_animation(anim_name):
		weapon_sprite.visible = true
		weapon_sprite.play(anim_name)


func _equip_weapon(idx: int) -> void:
	current_weapon_idx = idx
	var weapon: Dictionary = weapons[idx]
	weapon_label.text = weapon["name"].replace("_", " ").capitalize()

	# Load static weapon texture for held display
	var static_path: String = "res://assets/weapons/weapon_" + weapon["name"] + ".png"
	if ResourceLoader.exists(static_path):
		held_weapon.texture = load(static_path)
		held_weapon.visible = true
	else:
		held_weapon.visible = false


func _setup_weapon_animations() -> void:
	var frames := SpriteFrames.new()
	if frames.has_animation("default"):
		frames.remove_animation("default")

	for weapon: Dictionary in weapons:
		var anim_name: String = weapon["slash_file"]
		var tex_path: String = "res://assets/weapons/" + anim_name + ".png"

		if not ResourceLoader.exists(tex_path):
			continue

		frames.add_animation(anim_name)
		frames.set_animation_speed(anim_name, weapon["fps"])
		frames.set_animation_loop(anim_name, false)

		var sheet: Texture2D = load(tex_path)
		var frame_count: int = weapon["frames"]
		for i in frame_count:
			var atlas := AtlasTexture.new()
			atlas.atlas = sheet
			atlas.region = Rect2(i * 16, 0, 16, 16)
			frames.add_frame(anim_name, atlas)

	weapon_sprite.sprite_frames = frames
	weapon_sprite.visible = false


func _setup_animations() -> void:
	var frames := SpriteFrames.new()

	if frames.has_animation("default"):
		frames.remove_animation("default")

	var anims := {
		"idle": {"frames": 8, "fps": 6.7, "loop": true},
		"walk": {"frames": 8, "fps": 10.0, "loop": true},
		"run": {"frames": 8, "fps": 12.5, "loop": true},
		"attack": {"frames": 6, "fps": 11.3, "loop": false},
		"jump": {"frames": 4, "fps": 10.5, "loop": false},
		"hit": {"frames": 3, "fps": 12.5, "loop": false},
		"death": {"frames": 6, "fps": 8.0, "loop": false},
	}

	var dirs := ["down", "up", "right", "left"]

	for anim_name: String in anims:
		var info: Dictionary = anims[anim_name]
		for dir: String in dirs:
			var full_name: String = anim_name + "_" + dir
			var suffix: String = "_right_left" if dir == "left" else ("_" + dir)
			var tex_path: String = "res://assets/characters/player/player_" + anim_name + suffix + ".png"

			if not ResourceLoader.exists(tex_path):
				continue

			frames.add_animation(full_name)
			frames.set_animation_speed(full_name, info["fps"])
			frames.set_animation_loop(full_name, info["loop"])

			var sheet: Texture2D = load(tex_path)
			var frame_w := 16
			var frame_count: int = info["frames"]

			for i in frame_count:
				var atlas := AtlasTexture.new()
				atlas.atlas = sheet
				atlas.region = Rect2(i * frame_w, 0, frame_w, 16)
				frames.add_frame(full_name, atlas)

	sprite.sprite_frames = frames
	sprite.flip_h = false


func _process(_delta: float) -> void:
	sprite.flip_h = current_direction == "left"
	weapon_sprite.flip_h = current_direction == "left"
	held_weapon.flip_h = current_direction == "left"

	# Position weapon sprite (slash animation) relative to direction
	match current_direction:
		"right":
			weapon_sprite.position = Vector2(14, -8)
			held_weapon.position = Vector2(14, -4)
			held_weapon.rotation_degrees = -30.0
		"left":
			weapon_sprite.position = Vector2(-14, -8)
			held_weapon.position = Vector2(-14, -4)
			held_weapon.rotation_degrees = 30.0
		"down":
			weapon_sprite.position = Vector2(10, -2)
			held_weapon.position = Vector2(10, -2)
			held_weapon.rotation_degrees = -45.0
		"up":
			weapon_sprite.position = Vector2(-10, -14)
			held_weapon.position = Vector2(-10, -12)
			held_weapon.rotation_degrees = 45.0

	# Hide held weapon behind player when facing up
	if current_direction == "up":
		held_weapon.z_index = -1
	else:
		held_weapon.z_index = 1
