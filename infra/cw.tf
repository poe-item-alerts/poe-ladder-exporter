resource "aws_cloudwatch_event_rule" "poe_ladder_exporter" {
  name                = "poe_ladder_exporter"
  description         = "triggers the poe_ladder_exporter every minute"
  schedule_expression = var.cloudwatch_event_config["schedule"]
  is_enabled          = var.cloudwatch_event_config["enabled"]
  tags                = var.tags
}

resource "aws_cloudwatch_event_target" "poe_ladder_exporter" {
  target_id = "poe_ladder_exporter"
  rule      = aws_cloudwatch_event_rule.poe_ladder_exporter.name
  arn       = aws_lambda_function.poe_ladder_exporter.arn
}
