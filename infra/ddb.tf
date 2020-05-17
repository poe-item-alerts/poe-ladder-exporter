resource "aws_dynamodb_table" "poe_api_export_cache" {
  name         = "poe_item_alerts_characters"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "league"
  range_key    = "id"

  ttl {
    attribute_name = "ttl"
    enabled = true
  }

  attribute {
    name = "league"
    type = "S"
  }
  attribute {
    name = "id"
    type = "S"
  }
}

