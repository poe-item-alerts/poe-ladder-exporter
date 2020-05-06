resource "aws_lambda_function" "poe_ladder_exporter" {
  filename         = "../src/function-${var.commit_sha}.zip"
  function_name    = "poe_ladder_exporter"
  description      = "Exports the poe character window API into a cache"
  role             = aws_iam_role.poe_ladder_exporter.arn
  handler          = "poe_ladder_exporter.handler.handler"
  runtime          = var.lambda_config["runtime"]
  timeout          = var.lambda_config["timeout"]
  memory_size      = var.lambda_config["memory_size"]
  tags             = var.tags

  dead_letter_config {
    target_arn = aws_sns_topic.deadletter.arn
  }
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudwatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.poe_ladder_exporter.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.poe_ladder_exporter.arn
}
