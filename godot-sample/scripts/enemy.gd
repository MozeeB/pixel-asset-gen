extends CharacterBody2D

@export var enemy_type: String = "slime"
@export var wander_speed: float = 30.0
@export var wander_range: float = 50.0

var start_pos: Vector2
var wander_target: Vector2
var wander_timer: float = 0.0
var has_animations := false

@onready var sprite: AnimatedSprite2D = $AnimatedSprite2D


func _ready() -> void:
	start_pos = global_position
	_setup_animations()
	if has_animations:
		sprite.play("idle")
	_pick_wander_target()


func _physics_process(delta: float) -> void:
	wander_timer -= delta
	if wander_timer <= 0:
		_pick_wander_target()

	var dir := (wander_target - global_position)
	if dir.length() < 5.0:
		_pick_wander_target()
		velocity = Vector2.ZERO
	else:
		velocity = dir.normalized() * wander_speed
		# Flip sprite based on movement direction
		if dir.x < 0:
			sprite.flip_h = true
		elif dir.x > 0:
			sprite.flip_h = false

	move_and_slide()


func _pick_wander_target() -> void:
	wander_target = start_pos + Vector2(
		randf_range(-wander_range, wander_range),
		randf_range(-wander_range, wander_range)
	)
	wander_timer = randf_range(1.5, 4.0)


func _setup_animations() -> void:
	var frames := SpriteFrames.new()
	if frames.has_animation("default"):
		frames.remove_animation("default")

	var enemy_data := {
		"slime": {"idle_frames": 8, "idle_fps": 8.3},
		"skeleton": {"idle_frames": 4, "idle_fps": 5.0},
		"bat": {"idle_frames": 6, "idle_fps": 12.5},
		"ghost": {"idle_frames": 8, "idle_fps": 6.7},
		"goblin": {"idle_frames": 4, "idle_fps": 6.7},
	}

	var data: Dictionary = enemy_data.get(enemy_type, enemy_data["slime"])
	var tex_path := "res://assets/characters/enemies/" + enemy_type + ".png"

	if not ResourceLoader.exists(tex_path):
		sprite.sprite_frames = frames
		return

	frames.add_animation("idle")
	frames.set_animation_speed("idle", data["idle_fps"])
	frames.set_animation_loop("idle", true)

	var sheet: Texture2D = load(tex_path)
	var frame_count: int = data["idle_frames"]
	for i in frame_count:
		var atlas := AtlasTexture.new()
		atlas.atlas = sheet
		atlas.region = Rect2(i * 16, 0, 16, 16)
		frames.add_frame("idle", atlas)

	# Hit animation
	var hit_path := "res://assets/characters/enemies/" + enemy_type + "_hit.png"
	if ResourceLoader.exists(hit_path):
		frames.add_animation("hit")
		frames.set_animation_speed("hit", 12.5)
		frames.set_animation_loop("hit", false)
		var hit_sheet: Texture2D = load(hit_path)
		for i in 3:
			var atlas := AtlasTexture.new()
			atlas.atlas = hit_sheet
			atlas.region = Rect2(i * 16, 0, 16, 16)
			frames.add_frame("hit", atlas)

	# Death animation
	var death_path := "res://assets/characters/enemies/" + enemy_type + "_death.png"
	if ResourceLoader.exists(death_path):
		frames.add_animation("death")
		frames.set_animation_speed("death", 8.0)
		frames.set_animation_loop("death", false)
		var death_sheet: Texture2D = load(death_path)
		for i in 6:
			var atlas := AtlasTexture.new()
			atlas.atlas = death_sheet
			atlas.region = Rect2(i * 16, 0, 16, 16)
			frames.add_frame("death", atlas)

	sprite.sprite_frames = frames
	has_animations = true
