{
  apiVersion: 'v1',
  kind: 'Service',
  metadata: {
    name: 'data-catalog-backend',
  },
  spec: {
    ports: [{
      port: 80,
      targetPort: 8000,
    }],
    selector: {
      app: 'data-catalog-backend',
    },
  },
}