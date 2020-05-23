resource "aws_lambda_function" "poe_ladder_exporter" {
  filename      = "../src/poe_ladder_exporter-${var.commit_sha}.zip"
  function_name = "poe_ladder_exporter"
  description   = "Exports the poe character window API into a cache"
  role          = aws_iam_role.poe_ladder_exporter.arn
  handler       = "poe_ladder_exporter.handler.handler"
  runtime       = var.poe_ladder_lambda_config["runtime"]
  timeout       = var.poe_ladder_lambda_config["timeout"]
  memory_size   = var.poe_ladder_lambda_config["memory_size"]
  tags          = var.tags

  environment {
    variables = {
      LOG_LEVEL = var.poe_ladder_lambda_config["log_level"]
    }
  }

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

resource "aws_lambda_function" "poe_character_exporter" {
  filename      = "../src/poe_character_exporter-${var.commit_sha}.zip"
  function_name = "poe_character_exporter"
  description   = "Exports the poe character window API into a cache"
  role          = aws_iam_role.poe_character_exporter.arn
  handler       = "poe_character_exporter.handler.handler"
  runtime       = var.poe_character_lambda_config["runtime"]
  timeout       = var.poe_character_lambda_config["timeout"]
  memory_size   = var.poe_character_lambda_config["memory_size"]
  tags          = var.tags

  environment {
    variables = {
      LOG_LEVEL = var.poe_character_lambda_config["log_level"]
    }
  }

  dead_letter_config {
    target_arn = aws_sns_topic.deadletter.arn
  }
}

resource "aws_lambda_function" "poe_gravedigger" {
  filename      = "../src/poe_gravedigger-${var.commit_sha}.zip"
  function_name = "poe_gravedigger"
  description   = "Puts people in graves when they die :)"
  role          = aws_iam_role.poe_gravedigger.arn
  handler       = "handler.handler"
  runtime       = var.poe_gravedigger_lambda_config["runtime"]
  timeout       = var.poe_gravedigger_lambda_config["timeout"]
  memory_size   = var.poe_gravedigger_lambda_config["memory_size"]
  tags          = var.tags

  environment {
    variables = {
      LOG_LEVEL = var.poe_gravedigger_lambda_config["log_level"]
    }
  }

  dead_letter_config {
    target_arn = aws_sns_topic.deadletter.arn
  }
}
