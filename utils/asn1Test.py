import sys
import base64
import binascii
import utils.asn1 as asn1

def read_pem(input_file):
    """Read PEM formatted input."""
    data = []
    state = 0
    for line in input_file:
        if state == 0:
            if line.startswith('-----BEGIN'):
                state = 1
        elif state == 1:
            if line.startswith('-----END'):
                state = 2
            else:
                data.append(line)
        elif state == 2:
            break
    if state != 2:
        raise ValueError('No PEM encoded input found')
    data = ''.join(data)
    return base64.b64decode(data)

tag_id_to_string_map = {
    asn1.Numbers.Boolean: "BOOLEAN",
    asn1.Numbers.Integer: "INTEGER",
    asn1.Numbers.BitString: "BIT STRING",
    asn1.Numbers.OctetString: "OCTET STRING",
    asn1.Numbers.Null: "NULL",
    asn1.Numbers.ObjectIdentifier: "OBJECT",
    asn1.Numbers.PrintableString: "PRINTABLESTRING",
    asn1.Numbers.IA5String: "IA5STRING",
    asn1.Numbers.UTCTime: "UTCTIME",
    asn1.Numbers.Enumerated: "ENUMERATED",
    asn1.Numbers.Sequence: "SEQUENCE",
    asn1.Numbers.Set: "SET"
}

class_id_to_string_map = {
    asn1.Classes.Universal: "U",
    asn1.Classes.Application: "A",
    asn1.Classes.Context: "C",
    asn1.Classes.Private: "P"
}

object_id_to_string_map = {
    "1.2.840.113549.1.1.1": "rsaEncryption",
    "1.2.840.113549.1.1.5": "sha1WithRSAEncryption",

    "1.3.6.1.5.5.7.1.1": "authorityInfoAccess",

    "2.5.4.3": "commonName",
    "2.5.4.4": "surname",
    "2.5.4.5": "serialNumber",
    "2.5.4.6": "countryName",
    "2.5.4.7": "localityName",
    "2.5.4.8": "stateOrProvinceName",
    "2.5.4.9": "streetAddress",
    "2.5.4.10": "organizationName",
    "2.5.4.11": "organizationalUnitName",
    "2.5.4.12": "title",
    "2.5.4.13": "description",
    "2.5.4.42": "givenName",

    "1.2.840.113549.1.9.1": "emailAddress",

    "2.5.29.14": "X509v3 Subject Key Identifier",
    "2.5.29.15": "X509v3 Key Usage",
    "2.5.29.16": "X509v3 Private Key Usage Period",
    "2.5.29.17": "X509v3 Subject Alternative Name",
    "2.5.29.18": "X509v3 Issuer Alternative Name",
    "2.5.29.19": "X509v3 Basic Constraints",
    "2.5.29.30": "X509v3 Name Constraints",
    "2.5.29.31": "X509v3 CRL Distribution Points",
    "2.5.29.32": "X509v3 Certificate Policies Extension",
    "2.5.29.33": "X509v3 Policy Mappings",
    "2.5.29.35": "X509v3 Authority Key Identifier",
    "2.5.29.36": "X509v3 Policy Constraints",
    "2.5.29.37": "X509v3 Extended Key Usage"
}

def tag_id_to_string(identifier):
    """Return a string representation of a ASN.1 id."""
    if identifier in tag_id_to_string_map:
        return tag_id_to_string_map[identifier]
    return '{:#02x}'.format(identifier)


def class_id_to_string(identifier):
    """Return a string representation of an ASN.1 class."""
    if identifier in class_id_to_string_map:
        return class_id_to_string_map[identifier]
    raise ValueError('Illegal class: {:#02x}'.format(identifier))


def object_identifier_to_string(identifier):
    if identifier in object_id_to_string_map:
        return object_id_to_string_map[identifier]
    return identifier


def value_to_string(tag_number, value):
    if tag_number == asn1.Numbers.ObjectIdentifier:
        return object_identifier_to_string(value)
    elif isinstance(value, bytes):
        return '0x' + str(binascii.hexlify(value).upper())
    elif isinstance(value, str):
        return value
    else:
        return repr(value)


def pretty_print(input_stream, output_stream, indent=0):
    """Pretty print ASN.1 data."""
    while not input_stream.eof():
        tag = input_stream.peek()
        if tag.typ == asn1.Types.Primitive:
            tag, value = input_stream.read()
            output_stream.write(' ' * indent)
            output_stream.write('[{}] {}: {}\n'.format(class_id_to_string(tag.cls), tag_id_to_string(tag.nr), value_to_string(tag.nr, value)))
        elif tag.typ == asn1.Types.Constructed:
            output_stream.write(' ' * indent)
            output_stream.write('[{}] {}\n'.format(class_id_to_string(tag.cls), tag_id_to_string(tag.nr)))
            input_stream.enter()
            pretty_print(input_stream, output_stream, indent + 2)
            input_stream.leave()


if __name__ == '__main__':
    """ Do some self testing """
    input1 = b'00090080a600000800000005c004758f5f0008000340062f0042000a1811e1a30060047868c000180013000034000e050009090f800aef8b224fd3a389006b000518000c000000490020ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff002940040044f002004a40353401900102fc518004001072248244f93ffc4f93ffc4f93ffc4f93ffc4f93ffae07ee40441401190a70ca74a922020580000000000'
    input2 = b'0000008143000006000a000207f6000540021000000b00080044f00208579030001700070044f002e28042000e00810826186886f618000c0000ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff0311e1a30060047868c0000004400e4500090901f00af08ce337b3dbb780bb0a102fc518004001072248244f93ffc4f93ffc4f93ffc4f93ffc4f93ffae07ee40441401190a70ca74a9220205800000000015d8400003388410000708218014412ad38408a11d0dc406809f0dc60ca4568203000010044010c2362a6460dec07fea702e07fea7020fa89b80f5d4e2876213e601bbcca05cfe558ffd1535861c86c8a1844d06ad000000688000d100413016032fc02818210081844c236303e569d9228046039c8008000401e41229d4aaf2bdc801d0671810684a0044f002000f400c000044f000032fc020000003'
    input2 = b'0000008143000006000a000207f6000540021000000b00080044f00208579030001700070044f002e28042000e00810826186886f618000c0000ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff0311e1a30060047868c0000004400e4500090901f00af08ce337b3dbb780bb0a102fc518004001072248244f93ffc4f93ffc4f93ffc4f93ffc4f93ffae07ee40441401190a70ca74a9220205800000000015d8400003388410000708218014412ad38408a11d0dc406809f0dc60ca4568203000010044010c2362a6460dec07fea702e07fea7020fa89b80f5d4e2876213e601bbcca05cfe558ffd1535861c86c8a1844d06ad000000688000d100413016032fc02818210081844c236303e569d9228046039c8008000401e41229d4aaf2bdc801d0671810684a0044f002000f400c000044f000032fc020000003'
    input3 = open('../test/input.asn', 'rb').read()
    input4 = read_pem(open('../test/test.crt', 'r'))
    decoder = asn1.Decoder()
    
    l = len(input2)
    o = 0
    decoder.start(input2)
    pretty_print(decoder, sys.stdout)
    #while o < l:
    #    tt = decoder._read_tag()
    #    ll = decoder._read_length()
    #    print('type {} tag {} len {}, remaining {}'.format(asn1.Numbers(tt.nr).name, tt, ll, l - o))
    #    vv = decoder._read_value(tt.nr, ll)
    #    o += ll

    #pretty_print(decoder, sys.stdout)
