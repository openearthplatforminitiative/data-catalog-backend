{
  apiVersion: 'v1',
  kind: 'Service',
  metadata: {
    name: 'data-catalog-backend',
  },
  spec: {
    selector: {
      app: 'data-catalog-backend',
    },
    ports: [
      {
        name: 'public-api',
        port: 80,
        targetPort: 8000,
      },
      {
        name: 'admin-api',
        port: 81,
        targetPort: 8001,
      },
    ],
  },
}