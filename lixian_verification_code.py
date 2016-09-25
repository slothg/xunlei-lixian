
import platform
import sys
import readline

def file_path_verification_code_reader(path):
    def reader(image):
        with open(path, 'wb') as output:
            output.write(image)
        sys.stdout.write('Verification code picture is saved to %s, please open it manually and enter what you see.' % path)
        code = raw_input('Verification code: ')
        return code
    return reader


def ascii_verification_code_reader(image_data):
    import ascii_verification_code
    sys.stdout.write(ascii_verification_code.convert_to_ascii(image_data))
    sys.stdout.write('\n')
    code = raw_input('Verification code: ')
    return code


def ascii_imgcat_verification_code_reader(image_data):
    import os
    # os.system("imgcat << {:b}".format(image_data))
    path = os.path.join("/tmp/code.jpg")
    with open(path, "wb") as fb:
        fb.write(image_data)
    os.system("imgcat %s" % path)
    code = raw_input('Verification code: ')
    return code


def default_verification_code_reader(args):
    if args.verification_code_handler == 'ascii':
        return ascii_verification_code_reader
    elif args.verification_code_handler == 'terminal' and platform.system() == 'Darwin':
        return ascii_imgcat_verification_code_reader
    elif args.verification_code_path:
        return file_path_verification_code_reader(args.verification_code_path)
