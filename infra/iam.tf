resource "aws_iam_role" "poe_ladder_exporter" {
  name               = "poe_ladder_exporter_execution"
  assume_role_policy = file("policies/lambda_assume_role.json")
  tags               = var.tags
}

resource "aws_iam_policy" "poe_ladder_exporter_execution" {
  name        = "poe_ladder_exporter_execution"
  description = "Allows the lambda function to write to SNS for deadletter and to SQS for further components"
  policy      = file("policies/lambda_execution.json")
}

resource "aws_iam_role_policy_attachment" "poe_ladder_exporter" {
  role       = aws_iam_role.poe_ladder_exporter.name
  policy_arn = aws_iam_policy.poe_ladder_exporter_execution.arn
}

resource "aws_iam_role_policy_attachment" "poe_api_exporter_lambda_basic_execution" {
  role       = aws_iam_role.poe_ladder_exporter.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

