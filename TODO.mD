Domain
Domain name and region for your sending and receiving.

Tokyo
mindguard.com
Fill in your DNS Records
Add the following DNS records in your domain provider.
Domain Verification
DKIM
Type Name Content TTL Priority
TXT 
resend._domainkey
p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDf1blRgcsj7EigLyxm4GCK3n82ET/Qv99wNRofIMAFuFAmWREZ4FjuQK7azdMkpPt7XrT/5wxwGIhFklIesdk2XLaK0e1F4FQT24cTIlq/Cw11rWK+dLC1ldtwWLWGU8OsOJmeEL/zZGPfblHjgSjOV5cDp4pvFT+08+MLXK06SQIDAQAB
Auto 
Enable Sending

SPF
Type Name Content TTL Priority
MX 
send
feedback-smtp.ap-northeast-1.amazonses.com
Auto 10
TXT 
send
v=spf1 include:amazonses.com ~all
Auto 
DMARC
(Optional)
Type Name Content TTL Priority
TXT 
_dmarc
v=DMARC1; p=none;
Auto 
Enable Receiving

MX
Type Name Content TTL Priority
MX 
@
inbound-smtp.ap-northeast-1.amazonaws.com
Auto 10
