import { createClient } from "@/client";

export const dabblebase = createClient({
  projectId: "1",
  projectUrl: "http://localhost:3000",
  dabblebaseUrl: "http://localhost:8000",
  realtimeUrl: "http://localhost:4000",
  authVerifyKey:
    "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEApulw0mfxBaP7a+/JgYeBGQrB8r83oPzkWJCJWz6JgeUt18GmK3/u5EZtT+ZAPtszIOuhj/9Y7vpElVQyBnHpJdQ6BU2rV2cgdrT05B+HnXGOExMGwyzj8GWG+dtHpceytvMKj4q1hx5fwr90IUcWWq15xvG0py3u/FVqBocZLbQXVNsmcM+YGiULw+eD7S3R/BcbMHA8DjijidA1uLMr1VzhuuUk50lY17eBjGTsFegFBBmGCmj+07lTDobvHa2FD9mPampV9llou1ZCEAOTO4VDfcoYSGZ4QrfIEzNHVlbRPwlixq1QwIfTpMipX+lq3Xru0wkUc3BCwxeVHOFlwwIDAQAB",
  projectToken:
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwcm9qZWN0X2lkIjoxfQ.UPCBY66jbqwUJcjnrl1_3o9UnhlMnpuxIFDEnmd4iLk",
});
