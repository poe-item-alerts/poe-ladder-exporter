resource "aws_sns_topic" "deadletter" {
  name = "poe_ladder_exporter_deadletter"
  tags = var.tags
}
