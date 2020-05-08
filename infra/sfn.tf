resource "aws_sfn_state_machine" "character_loader" {
  name     = "poe_character_exporter"
  role_arn = aws_iam_role.poe_character_exporter_sfn.arn
  definition = templatefile(
    "data/step_function_definition.json",
    {
      lambda_arn = aws_lambda_function.poe_character_exporter.arn
    }
  )
  tags = var.tags
}
