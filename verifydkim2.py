import dkim
import argparse


def argbuilder():
    parser = argparse.ArgumentParser(description='Verify the DKIM signature in an email.')
    parser.add_argument('-t', dest='txt', metavar='TXT_Record', help='The DNS TXT value of the DKIM selector')
    parser.add_argument('-f', dest='txtfile', metavar='TXT_File', help='Same as \'-t\' except record is in a file')
    parser.add_argument('eml', metavar='email', help='The file containing the original raw email')

    args = parser.parse_args()
    return args


def mydns(name=None, timeout=None):
    return txtrecord


def verify():
    global txtrecord
    args = argbuilder()
    data = open(args.eml, 'rb').read()
    d = dkim.DKIM(message=data)
    if args.txt:
        txtrecord = args.txt
        ret = d.verify(dnsfunc=mydns)
    elif args.txtfile:
        txtrecord = open(args.txtfile, 'rb').read()
        ret = d.verify(dnsfunc=mydns)
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
