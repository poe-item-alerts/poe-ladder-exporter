data "archive_file" "poe_ladder_exporter" {
  type        = "zip"
  source_dir  = "../src/poe_ladder_exporter"
  output_path = "../src/poe_ladder_exporter.zip"
}

resource "aws_lambda_function" "poe_ladder_exporter" {
  filename         = "../src/poe_ladder_exporter.zip"
  function_name    = "poe_ladder_exporter"
  description      = "Exports the poe character window API into a cache"
  role             = aws_iam_role.poe_ladder_exporter.arn
  handler          = "handler.handler"
  source_code_hash = data.archive_file.poe_ladder_exporter.output_base64sha256
  runtime          = var.lambda_config["runtime"]
  timeout          = var.lambda_config["timeout"]
  memory_size      = var.lambda_config["memory_size"]
  tags             = var.tags

  dead_letter_config {
    target_arn = aws_sns_topic.deadletter.arn
  }

  depends_on = [data.archive_file.poe_ladder_exporter]
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudwatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.poe_ladder_exporter.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.poe_ladder_exporter.arn
}
