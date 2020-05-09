# resource "aws_appsync_graphql_api" "poe_ladder_export_api" {
#   authentication_type = "API_KEY"
#   name                = "poe_ladder_export"
# }

# resource "aws_appsync_datasource" "example" {
#   api_id           = aws_appsync_graphql_api.poe_ladder_export_api.id
#   name             = "tf_appsync_example"
#   service_role_arn = aws_iam_role.app_sync.arn
#   type             = "AMAZON_DYNAMODB"

#   dynamodb_config {
#     table_name = aws_dynamodb_table.poe_api_export_cache.name
#   }
# }
