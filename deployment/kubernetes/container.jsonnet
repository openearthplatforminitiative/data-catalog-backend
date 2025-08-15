{
  apiVersion: 'apps/v1',
  kind: 'Deployment',
  metadata: {
    name: 'data-catalog-backend',
    namespace: 'developer-portal',
  },
  spec: {
    replicas: 1,
    selector: {
      matchLabels: {
        app: 'data-catalog-backend',
      },
    },
    template: {
      metadata: {
        labels: {
          app: 'data-catalog-backend',
        },
      },
      spec: {
        initContainers: [{
          name: 'migrate-database',
          image: 'ghcr.io/openearthplatforminitiative/data-catalog-backend:0.1.2',
          imagePullPolicy: 'Always',
          envFrom: [{
            secretRef: {
              name: 'datacatalog-secrets',
            },
          }],
          env: [
            {
                name: 'RUN_MIGRATIONS',
                value: 'true'
            },
          ],
        }],
        containers: [{
          name: 'data-catalog-public-api',
          image: 'ghcr.io/openearthplatforminitiative/data-catalog-backend:0.1.2',
          imagePullPolicy: 'Always',
          ports: [{
            containerPort: 8000,
          }],
          envFrom: [{
            secretRef: {
              name: 'datacatalog-secrets',
            },
          }],
          env: [
            {
              name: 'API_DOMAIN',
              valueFrom: {
                configMapKeyRef: {
                  name: 'dev-portal-config',
                  key: 'api_domain'
                }
              }
            },
            {
                name: 'API_ROOT_PATH',
                value: '/catalog'
            },
            {
                name: 'INCLUDE_PUBLIC_API',
                value: 'true'
            },
            {
                name: 'UVICORN_PORT',
                value: '8000'
            }
          ],
        },
        {
          name: 'data-catalog-admin-api',
          image: 'ghcr.io/openearthplatforminitiative/data-catalog-backend:0.1.2',
          imagePullPolicy: 'Always',
          ports: [{
            containerPort: 8001,
          }],
          envFrom: [{
            secretRef: {
              name: 'datacatalog-secrets',
            },
          }],
          env: [
            {
              name: 'API_DOMAIN',
              valueFrom: {
                configMapKeyRef: {
                  name: 'dev-portal-config',
                  key: 'api_domain'
                }
              }
            },
            {
                name: 'API_ROOT_PATH',
                value: '/catalog'
            },
            {
                name: 'INCLUDE_PUBLIC_API',
                value: 'true'
            },
            {
                name: 'INCLUDE_ADMIN_API',
                value: 'true'
            },
            {
                name: 'UVICORN_PORT',
                value: '8001'
            }
          ],
        }],
      },
    },
  },
}