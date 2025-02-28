from aws_cdk import (
    CfnOutput,
    Duration,
    Stack,
    aws_apigatewayv2 as api_gateway,
    aws_apigatewayv2_integrations as integrations,
    aws_lambda as lambda_,
    aws_dynamodb as dynamodb,
)
from constructs import Construct

PRODUCTS_TABLE_NAME = "products"
STOCKS_TABLE_NAME = "stocks"


class ProductServiceStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        get_products_list_function = lambda_.Function(
            self,
            "GetProductsListLambda",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="get_products_list.lambda_handler",
            code=lambda_.Code.from_asset("lambda_func"),
            memory_size=128,
            timeout=Duration.seconds(5),
            environment={
                "PRODUCTS_TABLE_NAME": PRODUCTS_TABLE_NAME,
                "STOCKS_TABLE_NAME": STOCKS_TABLE_NAME,
            },
        )

        # Import existing DynamoDB tables
        products_table = dynamodb.Table.from_table_name(
            self, "ProductsTable", PRODUCTS_TABLE_NAME
        )
        stocks_table = dynamodb.Table.from_table_name(
            self, "StocksTable", STOCKS_TABLE_NAME
        )

        # Grant Lambda permissions to read from the tables
        products_table.grant_read_data(get_products_list_function)
        stocks_table.grant_read_data(get_products_list_function)

        get_product_by_id_function = lambda_.Function(
            self,
            "GetProductByIdLambda",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="get_products_by_id.lambda_handler",
            code=lambda_.Code.from_asset("lambda_func"),
            memory_size=128,
            timeout=Duration.seconds(5),
        )

        # Define API Gateway

        api = api_gateway.HttpApi(
            self,
            "ProductServiceApi",
            api_name="ProductServiceAPI",
            description="HTTP API for Product Service",
            cors_preflight=api_gateway.CorsPreflightOptions(
                allow_origins=[
                    "https://d3ewkax4tdopxb.cloudfront.net",
                    "http://localhost:3000",
                ],  # Allow CloudFront domain
                # allow_methods=["GET"],
                allow_headers=["*"],
            ),
        )

        api.add_routes(
            path="/products",
            methods=[api_gateway.HttpMethod.GET],
            integration=integrations.HttpLambdaIntegration(
                id="get_products_list", handler=get_products_list_function
            ),
        ),

        api.add_routes(
            path="/products/{productId}",
            methods=[api_gateway.HttpMethod.GET],
            integration=integrations.HttpLambdaIntegration(
                id="get_products_by_id",
                handler=get_product_by_id_function,
            ),
        )

        CfnOutput(self, "HttpApiUrl", value=api.url or "Unknown")
