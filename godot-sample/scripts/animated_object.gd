@tool
extends AnimatedSprite2D
## Generic animated sprite loader for pixel-asset-gen sprite sheets.
## Set sprite_path, frame_count, fps, and frame_size in the inspector.

@export var sprite_path: String = ""
@export var frame_count: int = 8
@export var fps: float = 8.0
@export var frame_size: Vector2i = Vector2i(16, 16)
@export var looping: bool = true
@export var auto_play: bool = true


func _ready() -> void:
	if sprite_path.is_empty():
		return
	_setup_animation()
	if auto_play:
		play("default")


func _setup_animation() -> void:
	if not ResourceLoader.exists(sprite_path):
		push_warning("Sprite not found: " + sprite_path)
		return

	var frames := SpriteFrames.new()
	if frames.has_animation("default"):
		frames.remove_animation("default")

	frames.add_animation("default")
	frames.set_animation_speed("default", fps)
	frames.set_animation_loop("default", looping)

	var sheet: Texture2D = load(sprite_path)
	for i in frame_count:
		var atlas := AtlasTexture.new()
		atlas.atlas = sheet
		atlas.region = Rect2(i * frame_size.x, 0, frame_size.x, frame_size.y)
		frames.add_frame("default", atlas)

	sprite_frames = frames
