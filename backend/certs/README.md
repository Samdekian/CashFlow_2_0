# Open Finance Brasil Certificates

This directory contains the certificates required for Open Finance Brasil integration.

## Required Certificates

### 1. Transport Certificate (`transport.pem`)
- **Purpose**: Client authentication for MTLS connections
- **Format**: X.509 certificate in PEM format
- **Usage**: Establishes secure connection with OFB APIs
- **Requirements**: Must be issued by a trusted CA recognized by Open Finance Brasil

### 2. Transport Private Key (`transport.key`)
- **Purpose**: Private key corresponding to transport certificate
- **Format**: RSA private key in PEM format
- **Security**: Keep this file secure and restrict access
- **Requirements**: Must match the transport certificate

### 3. Signing Certificate (`signing.pem`)
- **Purpose**: Certificate for signing JWT request objects (FAPI requirement)
- **Format**: X.509 certificate in PEM format
- **Usage**: Signs OAuth 2.0 request objects
- **Requirements**: Must be issued by a trusted CA

### 4. Signing Private Key (`signing.key`)
- **Purpose**: Private key for signing JWT request objects
- **Format**: RSA private key in PEM format
- **Security**: Keep this file secure and restrict access
- **Requirements**: Must match the signing certificate

### 5. CA Bundle (`ca-bundle.pem`)
- **Purpose**: Certificate Authority bundle for validation
- **Format**: Concatenated CA certificates in PEM format
- **Usage**: Validates server certificates and certificate chains
- **Requirements**: Must include OFB root and intermediate CAs

## Development Setup

For development and testing, you can use self-signed certificates:

```bash
# Generate transport certificate and key
openssl req -x509 -newkey rsa:4096 -keyout transport.key -out transport.pem -days 365 -nodes

# Generate signing certificate and key
openssl req -x509 -newkey rsa:4096 -keyout signing.key -out signing.pem -days 365 -nodes

# Create CA bundle (for development, you can use system CA bundle)
cp /etc/ssl/certs/ca-certificates.crt ca-bundle.pem
```

## Production Setup

For production use:

1. **Obtain Official Certificates**: Contact Open Finance Brasil for official certificates
2. **Certificate Authority**: Ensure certificates are issued by recognized CAs
3. **Key Management**: Use secure key management practices
4. **Certificate Renewal**: Monitor expiration dates and renew before expiry
5. **Security**: Restrict file permissions to authorized users only

## File Permissions

Set appropriate file permissions for security:

```bash
chmod 600 *.key          # Private keys: owner read/write only
chmod 644 *.pem          # Certificates: owner read/write, group/others read
chmod 644 ca-bundle.pem  # CA bundle: readable by all
```

## Environment Variables

Configure the following environment variables:

```bash
OFB_ENABLED=true
OFB_CLIENT_ID=your_client_id
OFB_CLIENT_SECRET=your_client_secret
OFB_REDIRECT_URI=https://yourdomain.com/ofb/callback
OFB_SANDBOX_MODE=true  # Set to false for production
```

## Validation

The system will automatically validate:
- Certificate existence
- Certificate expiration
- Certificate chain validation
- Private key matching

## Troubleshooting

Common issues:
1. **Certificate not found**: Check file paths in configuration
2. **Permission denied**: Verify file permissions
3. **Certificate expired**: Renew certificates
4. **Invalid certificate chain**: Update CA bundle
5. **Private key mismatch**: Ensure key matches certificate

## Security Notes

- Never commit private keys to version control
- Use environment variables for sensitive configuration
- Regularly rotate certificates
- Monitor certificate expiration
- Implement proper key management
- Follow security best practices for certificate storage
