extends CanvasLayer

@onready var hearts_container: HBoxContainer = $MarginContainer/HBoxContainer
@onready var controls_label: Label = $ControlsLabel


func _ready() -> void:
	_setup_hearts()
	_setup_controls_hint()


func _setup_hearts() -> void:
	var heart_tex := load("res://assets/ui/heart_full.png") as Texture2D
	var heart_empty_tex := load("res://assets/ui/heart_empty.png") as Texture2D

	if heart_tex == null:
		return

	for i in 5:
		var rect := TextureRect.new()
		rect.texture = heart_tex if i < 3 else heart_empty_tex
		rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		rect.custom_minimum_size = Vector2(32, 32)
		rect.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		hearts_container.add_child(rect)


func _setup_controls_hint() -> void:
	controls_label.text = "Arrow Keys: Move | Shift: Run | Space: Attack | Q/E: Switch Weapon"
