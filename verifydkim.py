# License information retrieved from https://launchpad.net/dkimpy since
# the Class created here is derived from dkimpy source code. Two functions
# were altered to override default functionality to suit my needs:
#
# This software is provided 'as-is', without any express or implied
# warranty. In no event will the author be held liable for any damages
# arising from the use of this software.
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
# 1. The origin of this software must not be misrepresented; you must not
# claim that you wrote the original software. If you use this software
# in a product, an acknowledgment in the product documentation would be
# appreciated but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
# misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.)
#

import dkim
import argparse


class MyDKIM(dkim.DKIM):
    # Define new __init__() function with our new field "txtrecord" added in front
    def __init__(self, txtrecord=None, message=None, logger=None, signature_algorithm=b'rsa-sha256',
                 minkey=1024, linesep=b'\r\n', debug_content=False, timeout=5, tlsrpt=False):

        # Inherit the __init__() function of the parent class
        super().__init__(message=None, logger=None, signature_algorithm=b'rsa-sha256', minkey=1024,
                         linesep=b'\r\n', debug_content=False, timeout=5, tlsrpt=False)

        self.txtrecord = txtrecord
        self.set_message(message)

    # This is taken from dkim.load_pk_from_dns and copied into this class
    # It has been altered to provide the flexibility of using dns or using a pubkey provided manually
    def load_pk_from_dns(self, name, dnsfunc=dkim.get_txt, timeout=5):
        if dnsfunc is None:
            s = self.txtrecord
        else:
            s = dnsfunc(name, timeout=timeout)
        pk, keysize, ktag, seqtlsrpt = dkim.evaluate_pk(name, s)
        return pk, keysize, ktag, seqtlsrpt

    # This overrides the function in the DomainSigner class so that it could be altered to
    # call self.load_pk_from_dns defined above instead of dkim.load_pk_from_dns.
    # See line 3 & 4 of this function. It is the only change that was made to it.
    def verify_sig(self, sig, include_headers, sig_header, dnsfunc):
        name = sig[b's'] + b"._domainkey." + sig[b'd'] + b"."
        try:
            self.pk, self.keysize, self.ktag, self.seqtlsrpt = \
                self.load_pk_from_dns(name, dnsfunc, timeout=self.timeout)
        except dkim.KeyFormatError as e:
            self.logger.error("%s" % e)
            return False
        except dkim.binascii.Error as e:
            self.logger.error('KeyFormatError: {0}'.format(e))
            return False
        return self.verify_sig_process(sig, include_headers, sig_header, dnsfunc)


def argbuilder():
    parser = argparse.ArgumentParser(description='Verify the DKIM signature in an email.')
    parser.add_argument('-t', dest='txt', metavar='TXT_Record', help='The DNS TXT value of the DKIM selector')
    parser.add_argument('-f', dest='txtfile', metavar='TXT_File', help='Same as \'-t\' except record is in a file')
    parser.add_argument('eml', metavar='email', help='The file containing the original raw email')

    args = parser.parse_args()
    return args


def verify():
    args = argbuilder()
    data = open(args.eml, 'rb').read()
    d = MyDKIM(message=data)
    if args.txt:
        d.txtrecord = args.txt
        ret = d.verify(dnsfunc=None)
    elif args.txtfile:
        d.txtrecord = open(args.txtfile, 'rb').read()
        ret = d.verify(dnsfunc=None)
    else:
        ret = d.verify()
    return ret


if __name__ == "__main__":
    if verify():
        print('DKIM verification succeeded.')
        exit(0)
    else:
        print('DKIM verification failed.')
        exit(1)
