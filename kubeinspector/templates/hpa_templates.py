def generate_complete_hpa(target_deployment: str, namespace: str) -> dict:
    """
    Generate a fully-featured HPA with all the bells and whistles.
    """
    return {
        "apiVersion": "autoscaling/v2",
        "kind": "HorizontalPodAutoscaler",
        "metadata": {
            "name": f"{target_deployment}-hpa",
            "namespace": namespace
        },
        "spec": {
            "scaleTargetRef": {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "name": target_deployment
            },
            "minReplicas": 2,
            "maxReplicas": 10,
            "metrics": [
                {
                    "type": "Resource",
                    "resource": {
                        "name": "cpu",
                        "target": {
                            "type": "Utilization",
                            "averageUtilization": 70
                        }
                    }
                },
                {
                    "type": "Resource",
                    "resource": {
                        "name": "memory",
                        "target": {
                            "type": "Utilization",
                            "averageUtilization": 80
                        }
                    }
                }
            ],
            "behavior": {
                "scaleDown": {
                    "stabilizationWindowSeconds": 300,
                    "policies": [
                        {
                            "type": "Percent",
                            "value": 50,
                            "periodSeconds": 60
                        }
                    ]
                },
                "scaleUp": {
                    "stabilizationWindowSeconds": 0,
                    "policies": [
                        {
                            "type": "Percent",
                            "value": 100,
                            "periodSeconds": 15
                        },
                        {
                            "type": "Pods",
                            "value": 4,
                            "periodSeconds": 15
                        }
                    ],
                    "selectPolicy": "Max"
                }
            }
        }
    }

def generate_custom_metric_hpa_patch(metric_type: str, target_value: str) -> dict:
    if metric_type == 'rps':
        return {
            "type": "Object",
            "object": {
                "metric": {
                    "name": "requests_per_second"
                },
                "describedObject": {
                    "apiVersion": "networking.k8s.io/v1",
                    "kind": "Ingress",
                    "name": "{{ .TargetDeployment }}"
                },
                "target": {
                    "type": "AverageValue",
                    "averageValue": target_value
                }
            }
        }
    elif metric_type == 'latency':
        return {
            "type": "Object",
            "object": {
                "metric": {
                    "name": "request_latency_p95"
                },
                "describedObject": {
                    "apiVersion": "networking.k8s.io/v1",
                    "kind": "Ingress",
                    "name": "{{ .TargetDeployment }}"
                },
                "target": {
                    "type": "AverageValue",
                    "averageValue": target_value
                }
            }
        }
