resource "aws_iam_role" "poe_ladder_exporter" {
  name               = "poe_ladder_exporter_execution"
  assume_role_policy = file("policies/lambda_assume_role.json")
  tags               = var.tags
}

resource "aws_iam_policy" "poe_ladder_exporter_execution" {
  name        = "poe_ladder_exporter_execution"
  description = "Allows the lambda function to write to SNS for deadletter and to SQS for further components"
  policy      = file("policies/poe_ladder_exporter.json")
}

resource "aws_iam_role_policy_attachment" "poe_ladder_exporter" {
  role       = aws_iam_role.poe_ladder_exporter.name
  policy_arn = aws_iam_policy.poe_ladder_exporter_execution.arn
}

resource "aws_iam_role_policy_attachment" "poe_api_exporter_lambda_basic_execution" {
  role       = aws_iam_role.poe_ladder_exporter.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role" "poe_character_exporter" {
  name               = "poe_character_exporter_execution"
  assume_role_policy = file("policies/lambda_assume_role.json")
  tags               = var.tags
}

resource "aws_iam_policy" "poe_character_exporter_execution" {
  name        = "poe_character_exporter_execution"
  description = "Allows the lambda function to write to SNS for deadletter and to dynamo db"
  policy      = file("policies/poe_character_exporter.json")
}

resource "aws_iam_role_policy_attachment" "poe_character_exporter" {
  role       = aws_iam_role.poe_character_exporter.name
  policy_arn = aws_iam_policy.poe_character_exporter_execution.arn
}

resource "aws_iam_role_policy_attachment" "poe_character_exporter_lambda_basic_execution" {
  role       = aws_iam_role.poe_character_exporter.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role" "poe_character_exporter_sfn" {
  name               = "poe_character_exporter_execution_sfn"
  assume_role_policy = file("policies/sfn_assume_role.json")
  tags               = var.tags
}

resource "aws_iam_policy" "poe_character_exporter_sfn" {
  name        = "poe_character_exporter_sfn"
  description = "Allows the step functions to invoke lambdas"
  policy      = file("policies/poe_character_exporter_sfn.json")
}

resource "aws_iam_role_policy_attachment" "poe_character_exporter_sfn" {
  role       = aws_iam_role.poe_character_exporter_sfn.name
  policy_arn = aws_iam_policy.poe_character_exporter_sfn.arn
}

resource "aws_iam_role" "app_sync" {
  name               = "poe_ladder_export_app_sync"
  assume_role_policy = file("policies/app_sync_assume_role.json")
  tags               = var.tags
}

resource "aws_iam_policy" "app_sync" {
  name        = "poe_ladder_export_app_sync"
  description = "Allows app sync to handle the dynamoDB table"
  policy      = templatefile("policies/app_sync.json", {ddb_table=aws_dynamodb_table.poe_api_export_cache.arn})
}

resource "aws_iam_role_policy_attachment" "app_sync" {
  role       = aws_iam_role.app_sync.name
  policy_arn = aws_iam_policy.app_sync.arn
}
