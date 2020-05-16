resource "aws_appsync_graphql_api" "poe_ladder_export_api" {
  authentication_type = "API_KEY"
  name                = "poe_ladder_export"
  schema              = file("data/graphql_schema")
}

resource "aws_appsync_datasource" "ladder_table" {
  api_id           = aws_appsync_graphql_api.poe_ladder_export_api.id
  name             = "ladder_table"
  service_role_arn = aws_iam_role.app_sync.arn
  type             = "AMAZON_DYNAMODB"

  dynamodb_config {
    table_name = aws_dynamodb_table.poe_api_export_cache.name
  }
}

resource "aws_appsync_resolver" "list_items" {
  api_id            = aws_appsync_graphql_api.poe_ladder_export_api.id
  field             = "listItems"
  type              = "Query"
  data_source       = aws_appsync_datasource.ladder_table.name
  request_template  = file("data/list_request_mapping")
  response_template = file("data/list_response_mapping")
}

resource "aws_appsync_api_key" "temporary" {
  api_id      = aws_appsync_graphql_api.poe_ladder_export_api.id
  description = "Need to figure out key cycling (probably the search lambdas will just authenticate through IAM tho I'm so tired)"
}
