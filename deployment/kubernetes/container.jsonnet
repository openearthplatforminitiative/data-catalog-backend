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
        containers: [{
          name: 'data-catalog-backend',
          image: 'ghcr.io/openearthplatforminitiative/data-catalog-backend:0.0.1-SNAPSHOT',
          imagePullPolicy: 'Always',
          ports: [{
            containerPort: 8000,
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
              name: 'POSTGRES_HOST',
              valueFrom: {
                secretKeyRef: {
                  name: 'datacatalog-db',
                  key: 'host',
                },
              },
            },
            {
              name: 'POSTGRES_PORT',
              valueFrom: {
                secretKeyRef: {
                  name: 'datacatalog-db',
                  key: 'port',
                },
              },
            },
            {
              name: 'POSTGRES_DB',
              valueFrom: {
                secretKeyRef: {
                  name: 'datacatalog-db',
                  key: 'database',
                },
              },
            },
            {
              name: 'POSTGRES_USER',
              valueFrom: {
                secretKeyRef: {
                  name: 'datacatalog-db',
                  key: 'user',
                },
              },
            },
            {
              name: 'POSTGRES_PASSWORD',
              valueFrom: {
                secretKeyRef: {
                  name: 'datacatalog-db',
                  key: 'password',
                },
              },
            },
          ],
        }],
      },
    },
  },
}