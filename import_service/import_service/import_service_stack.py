from aws_cdk import (
    # Duration,
    Stack,
    aws_apigatewayv2 as apigateway,
    aws_apigatewayv2_integrations as integrations,
    aws_lambda as lambda_,
)
from constructs import Construct

S3_BUCKET_NAME = "uploaded"


class ImportServiceStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        import_function = lambda_.Function(
            self, "ImportProductsFileLambda",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="import_products.lambda_handler",
            code=lambda_.Code.from_asset("lambda_func"),
            environment={
                "S3_BUCKET_NAME": S3_BUCKET_NAME,
            }
        )

        api = apigateway.HttpApi(
            self, "ImportServiceAPI",
        )

        api.add_routes(
            path="/import",
            methods=[apigateway.HttpMethod.GET],
            integration=integrations.HttpLambdaIntegration(
                "ImportProductsFileIntegration", import_function
            )
        )
