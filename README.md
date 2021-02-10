# Why
I made this so that I could have a way of verifying DKIM signatures on raw email files. While there is plenty of code out there that does this, I wanted it to be

    1: Python and 
    2: Flexible enough that I don't have to rely on a DNS query for it to function.

The reason for #2 is this:  
We always hear about cyber security compromises where this was leaked and that was leaked and sometimes the thing that is leaked is an email. It's all over social media or the news or whatever. The leaked email is typically posted somewhere and inevitably, security professionals will want to verify the authenticity of said leaked email. When the source of the email contains a DKIM signature block, we can do this. But what if the email is so old that the DKIM record in the public DNS has been changed? It's possible my google-foo has just failed me however, the only Python libs I can find out there rely on DNS in order to verify the signature. That’s a problem if the TXT record has been changed in the 5 years it’s been since the email was originally signed. For this we need access to historical DNS records like DomainTools or SecurityTrails. Once we find the historical DNS record, we need to have the DKIM verification code use that record instead of the one supplied by a typical DNS query.

dkimpy 1.0.5 can be installed with pip and as of this writing, it is the latest version.  
Developers site is here: https://launchpad.net/dkimpy

While following the execution of dkimpy I learned that the dnsfunc parameter is flexible. You can specify other dns functions beside being stuck with the one provided. Following some more I found exactly where the DNS response emerges with the TXT record and supplies said record to the rest of the code. The dnsfunc parameter "expects" a callable function. Editing the source code to accept a string instead of a function may have broken other things in the course of making my code work so, I learned about Python classes and how to inherit functionality etc. Yup, it was a fine time for some hands-on-learning.

verifydkim.py contains a new class that inherits the functionality of the original dkimpy code. Additionally, there are two functions that effectively override the behavior of the originals and provide more flexibility. That flexibility being: Do I want to use the built in DNS function or do I want to forego that and just tell it exactly what public key to use.

Python 3 is required


```
python.exe verifydkim.py -h
usage: verifydkim.py [-h] [-t TXT_Record] [-f TXT_File] email

Verify the DKIM signature in an email.

positional arguments:
  email          The file containing the original raw email

optional arguments:
  -h, --help     show this help message and exit
  -t TXT_Record  The DNS TXT value of the DKIM selector
  -f TXT_File    Same as '-t' except record is in a file
```
Example:
```
python.exe verifydkim.py some.eml -t "k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDGoQCNwAQdJBy23MrShs1EuHqK/dtDC33QrTqgWd9CJmtM3CK2ZiTYugkhcxnkEtGbzg+IJqcDRNkZHyoRezTf6QbinBB2dbyANEuwKI5DVRBFowQOj9zvM3IvxAEboMlb0szUjAoML94HOkKuGuCkdZ1gbVEi3GcVwrIQphal1QIDAQAB"

DKIM verification succeeded.
```
The value of -t may also have been placed in a file and then we would use -f instead:
```
python.exe verifydkim.py some.eml -f sometxtrecord.txt

DKIM verification succeeded.
```

# What happens during DKIM verification
This is a high-level overview of what is analyzed and how things are computed during a DKIM verification check. Take the following email (names have been changed to protect the ~~innocent~~ guilty). Observe this partial email header:

```
Received: by mail-il1-f169.google.com with SMTP id e7s555555f2ile.7
        for <redacted@redacted.net>; Tue, 09 Feb 2021 17:23:57 -0800 (PST)
DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed;
        d=gmail.com; s=20161025;
        h=from:mime-version:date:message-id:subject:to;
        bh=YOkovY1y1GXe8mYwThyvrMFN03ECH7w+Vd39CZAkvUo=;
        b=AJAVtcVaChkBCxbsUJtx7CZaQ9jx8z6wNf7g46llKKcGHbuXqwHnvHGuOHbNb65K8j
         b3WqyTs82MHZBdKFwu0V/kjD6f1kanypV5caGdbDzZ/mMs1nu2Y0CpFrZep5bm2OG1En
         +1JwbJk3JzfHdJqEYylqUbMFUJKKMrqLoZUMCV4CP8KEp8j9jkY2wh7kDhRdRdPK77If
         mY8gk+wpMh1DsZOTV9Jp3EpADNumev4i/Zq1T0jPyRMQb8fRBwIisES5Zc1ISVb0OTB7
         9YPKanvKCWYM/eYS1cE6D5+Ca45u0Py+pplAI4GiAyDEvCTnI+Y23YE9t1rQ2YoHbeTG
         5q/g==
X-Google-Smtp-Source: ABdhPJwDBWhwWltCrJLbful0oQYX1kqCsCdeSArP57QW7+OJHiM0rUI9oCqfuW0mhNsZOtwzaVn+fuAHUR79xTgohIQ=
X-Received: by 2002:a92:d0d:: with SMTP id 13mr666666iln.36.1612966666656;
 Tue, 09 Feb 2021 17:23:56 -0800 (PST)
Received: from 218666660171 named unknown by gmailapi.google.com with
 HTTPREST; Tue, 9 Feb 2021 20:23:56 -0500
From: Some Person <redacted@gmail.com>
MIME-Version: 1.0
Date: Tue, 9 Feb 2021 20:23:56 -0500
Message-ID: <CAJj9PrvNj0Yp6666666666+KQ1E2t8VaMrT6wgLz_Dt+BMULWQ@mail.gmail.com>
Subject: It's been awhile
To: redacted@redacted.net
Content-Type: multipart/alternative; boundary="000000000000c16666666f141c2"
X-CMAE-Envelope: MS4xfBj3EuJfiICBSOVDKHn4ag0vFBvtzwVZ0+s0Jzpnzwd3+QnaOlcBlS5fbtJpkSd3C2ObAruSIy1sWpcHJky1cufLKZrvIsCugZF3+WE0n25DEuRpzJPL
 oONVmNiRXM232JfR7w5WaZw6i5uqmD/vo/mgKPChlDmFuCZSSPG3ZNxcFwSgfWiATvL9KhAV67auSS80/KIpw1NKkJDI3qXrIl8=
```
The things to be concerned with are here:
```
DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed;
        d=gmail.com; s=20161025;
        h=from:mime-version:date:message-id:subject:to;
        bh=YOkovY1y1GXe8mYwThyvrMFN03ECH7w+Vd39CZAkvUo=;
        b=AJAVtcVaChkBCxbsUJtx7CZaQ9jx8z6wNf7g46llKKcGHbuXqwHnvHGuOHbNb65K8j
         b3WqyTs82MHZBdKFwu0V/kjD6f1kanypV5caGdbDzZ/mMs1nu2Y0CpFrZep5bm2OG1En
         +1JwbJk3JzfHdJqEYylqUbMFUJKKMrqLoZUMCV4CP8KEp8j9jkY2wh7kDhRdRdPK77If
         mY8gk+wpMh1DsZOTV9Jp3EpADNumev4i/Zq1T0jPyRMQb8fRBwIisES5Zc1ISVb0OTB7
         9YPKanvKCWYM/eYS1cE6D5+Ca45u0Py+pplAI4GiAyDEvCTnI+Y23YE9t1rQ2YoHbeTG
         5q/g==
```
In the above code block we have the DKIM version, the signing algorithm used (rsa encryption and sha256 hashing), how the header and body was canonicalized (relaxed/relaxed) before being analyzed, the domain, the selector, the headers involved in the signing process, the base64 encoded hash of the emails body section and lastly, the tag "b" which will contain the base64 encoded DKIM signature.

The first step in the verification process is to verify the "bh" tag. This is the hash of the emails body. Everything including attachments that follow the headers is hashed using the algorithm specified in the "a" tag. In this case a SHA256 hash is computed for the body then base64 encoded. The resulting value better match the value of "bh" or the process fails immediately and no more checks need to be done.

Assuming all went well, the next step is to assemble the headers specified in the "h" tag. This tells DKIM which headers are being included in the signing process. The headers are assembled "in the order they appear in the 'h' tag". So, given the value of the "h" tag, build a list that looks like this:
```
from:Some Person <redacted@gmail.com>
mime-version:1.0
date:Tue, 9 Feb 2021 20:23:56 -0500
message-id:<CAJj9PrvNj0Yp6666666666+KQ1E2t8VaMrT6wgLz_Dt+BMULWQ@mail.gmail.com>
subject:It's been awhile
to:redacted@redacted.net
```
Then append this to the bottom of that list:
```
dkim-signature:v=1; a=rsa-sha256; c=relaxed/relaxed; d=gmail.com; s=20161025; h=from:mime-version:date:message-id:subject:to; bh=YOkovY1y1GXe8mYwThyvrMFN03ECH7w+Vd39CZAkvUo=; b=
```
Note that I converted all the header names to lowercase. This is because the canonicalization was set to "relaxed" in the "c" tag. Also I removed all CRLF characters from the dkim-signature header and removed all repeating whitespace (aka: folding). The block of text now consists of 7 lines; from the "from" field to the "dkim-signature" field. There is "no CRLF" at the end of the "b=". This data is then hashed to produce a 32 byte string that is the SHA256 hash of the data.  
Let's call that hash "x" for now. We'll need it in a minute.

To complete the next step we are going to need the public key because it contains the public exponent and the modulus that corresponds to the private key used to sign this data. That is retrieved via DNS. Anyone can do it:
```
dig TXT 20161025._domainkey.gmail.com
```
I got that FQDN by looking at the "s" tag and the "d" tag in the header and then inserted "\_domainkey" right in between them.

At this point we need to look at the data that shipped with the email that was in the "b" tag. That data needs to be base64 decoded, converted to a long integer, raised to the power of the public keys exponent and modded by the public keys modulus. Psuedo code: pow(bytes2longint(base64decode(btag)), pub['e'], pub['n']).  
We'll call this result "y". This should be equal to the hash before it was raised to the power of the "private" exponent and base64 encoded.

```
If x != y:
  we have a problem
  exit()
```
# A final note on DKIM
While it's true that only headers are signed during the DKIM signing process I should remind you that 1 of those pieces of the signed header data is the "bh" tag. A person new to DKIM might think that since only the headers are signed, that they can somehow change the body without affecting the signature. They might think "Hey I can change the body, then just change the bh tag to match the new hash!". That would definately get you past step 1 of the verification process but would cause a verification failure in the next steps. Because during the next steps, the "bh" tag and its value were signed during the signing process on the headers. So while the body of the email isn't signed, it's hash IS signed. This is suffcient to assert that neither the involved headers of any part of the body has been altered since the email was originally sent.
