from aws_cdk import (
    CfnOutput,
    Duration,
    Stack,
    aws_apigatewayv2 as api_gateway,
    aws_apigatewayv2_integrations as integrations,
    aws_lambda as lambda_,
)
from constructs import Construct


class ProductServiceStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        get_products_list_function = lambda_.Function(
            self,
            "GetProductsListLambda",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="get_products_list.lambda_handler",
            code=lambda_.Code.from_asset("lambda"),
            timeout=Duration.seconds(10),
        )

        # Define API Gateway

        api = api_gateway.HttpApi(
            self,
            "ProductServiceApi",
            api_name="ProductServiceAPI",
            description="HTTP API for Product Service",
        )

        api.add_routes(
            path="/products",
            methods=[api_gateway.HttpMethod.GET],
            integration=integrations.HttpLambdaIntegration(
                id="get_products_list",
                handler=get_products_list_function
            ),
        ),

        CfnOutput(self, "HttpApiUrl", value=api.url or "Unknown")



