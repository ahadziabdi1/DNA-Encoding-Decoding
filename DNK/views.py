from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from .forms import FileUploadForm
import binascii
from django.views.decorators.csrf import csrf_protect
import mimetypes

def DNK_Encode(source):
    # 00 - C
    # 01 - T
    # 10 - A
    # 11 - G
    source = source.replace(" ", "")

    if len(source)%2 == 1:
        source = "0" + source

    code = ""
    for i in range(0, len(source), 2):
        coded_nucleotid = source[i:i+2]

        nucleotid = "C"
        if coded_nucleotid == "01":
            nucleotid = "T"
        elif coded_nucleotid == "10":
            nucleotid = "A"
        elif coded_nucleotid == "11":
            nucleotid = "G"

        code += nucleotid

    return code

def DNK_Decode(source):
    # 00 - C
    # 01 - T
    # 10 - A
    # 11 - G
    
    source = source.replace(" ", "")

    decode = ""
    for char in source:
        
        decoded_nucleotid = chr(ord(char))

        nucleotid = "00"
        if decoded_nucleotid == "T":
            nucleotid = "01"
        elif decoded_nucleotid == "A":
            nucleotid = "10"
        elif decoded_nucleotid == "G":
            nucleotid = "11"

        decode += nucleotid

    return decode


def home(request):
    binary_string = ""
    encoded_data = ""
    decoded_data = ""

    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            action_type = request.POST.get('action_type', '')
            file_bytes = file.read()

            if action_type == 'code': 
                path_bytes = file.name.encode()

                binary_data = path_bytes + b'\n' + file_bytes
                hex_string = binascii.hexlify(binary_data)
                binary_string = bin(int(hex_string, 16))[2:]

                encoded_data = DNK_Encode(binary_string)
            
            elif action_type == 'decode':
                decoded_data = DNK_Decode(file_bytes.decode())


    else:
        form = FileUploadForm()

    context = {
        'form': form,
        'encoded_data': encoded_data,
        'decoded_data': decoded_data
    }

    return render(request, 'home.html', context)

def download_file(request):
    if request.method == 'POST':
        

        file_contents = request.POST.get('file_contents_encoded', '')

        if file_contents != "":
            response = HttpResponse(file_contents, content_type='text/plain')
            response['Content-Disposition'] = 'attachment; filename="coded_file.txt"'

        else:
            file_contents = request.POST.get('file_contents_decoded', '')
            binary_data = bytes([int(file_contents[i:i+8], 2) for i in range(0, len(file_contents), 8)])
            lines = binary_data.split(b'\n')

            first_line = lines[0].decode('utf-8')
            binary_data = b'\n'.join(lines[1:])

            content_type = mimetypes.guess_type(first_line)[0]


            response = HttpResponse(binary_data, content_type=content_type)
            response['Content-Disposition'] = 'attachment; filename="%s"' % first_line
        return response
    else:
        return HttpResponseBadRequest('Invalid request method')