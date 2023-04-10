import os
import time
import threading
import glob
import fractions
import cv2
import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms
from SimSwap.models.models import create_model
from SimSwap.insightface_func.face_detect_crop_single import Face_detect_crop
from SimSwap.util.reverse2stream import reverse2wholeimage
from SimSwap.util.add_watermark import watermark_image
from SimSwap.util.norm import SpecificNorm
from SimSwap.parsing_model.model import BiSeNet

outputFrame = None
lock = threading.Lock()
is_started = False
RECONNECTION_TIMEOUT = 30

def lcm(a, b): return abs(a * b) / fractions.gcd(a, b) if a and b else 0

transformer_Arcface = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

def _totensor(array):
    tensor = torch.from_numpy(array)
    img = tensor.transpose(0, 1).transpose(0, 2).contiguous()
    return img.float().div(255)

def streamer(app, swap_model, opt):
    global outputFrame, lock, is_started

    start_epoch, epoch_iter = 1, 0
    crop_size = opt.crop_size
    logoclass = watermark_image('./simswaplogo/simswaplogo.png')

    spNorm = SpecificNorm()
    with torch.no_grad():
        pic_a = opt.pic_a_path
        img_a_whole = cv2.imread(pic_a)
        img_a_align_crop, _ = app.get(img_a_whole,crop_size)
        img_a_align_crop_pil = Image.fromarray(cv2.cvtColor(img_a_align_crop[0],cv2.COLOR_BGR2RGB)) 
        img_a = transformer_Arcface(img_a_align_crop_pil)
        img_id = img_a.view(-1, img_a.shape[0], img_a.shape[1], img_a.shape[2])

        # convert numpy to tensor
        img_id = img_id.cuda()

        #create latent id
        img_id_downsample = F.interpolate(img_id, size=(112,112))
        latend_id = swap_model.netArc(img_id_downsample)
        latend_id = F.normalize(latend_id, p=2, dim=1)
        placeholder = cv2.imread('./resources/no-signal.jpg')
        placeholderOk, encodedPlacehodler = cv2.imencode(".jpg", placeholder)

        pic_b = opt.pic_b_path
        try:
            capture = cv2.VideoCapture(pic_b)
            if opt.use_mask:
                n_classes = 19
                net = BiSeNet(n_classes=n_classes)
                net.cuda()
                save_pth = os.path.join('./parsing_model/checkpoint', '79999_iter.pth')
                net.load_state_dict(torch.load(save_pth))
                net.eval()
            else:
                net = None

            while(True):
                if not is_started:
                    break
                if not capture.isOpened():
                    outputFrame = encodedPlacehodler
                    raise ConnectionError
                #vsFrame = vs.read()
                hasFrame, img_b_whole = capture.read()

                if not hasFrame:
                    outputFrame = encodedPlacehodler
                    continue
                 
                #_enc, encodedImage = cv2.imencode(".jpg", img_b_whole)
                #outputFrame = encodedImage
                #continue
                ############## Forward Pass ######################

                #img_b_whole = cv2.imread(pic_b)
                target_results = app.get(img_b_whole,crop_size)
                with lock:
                    if target_results:
                      img_b_align_crop_list, b_mat_list = target_results            # detect_results = None
                      swap_result_list = []

                      b_align_crop_tenor_list = []

                      for b_align_crop in img_b_align_crop_list:

                          b_align_crop_tenor = _totensor(cv2.cvtColor(b_align_crop,cv2.COLOR_BGR2RGB))[None,...].cuda()

                          swap_result = swap_model(None, b_align_crop_tenor, latend_id, None, True)[0]
                          swap_result_list.append(swap_result)
                          b_align_crop_tenor_list.append(b_align_crop_tenor)

                      outputFrame = reverse2wholeimage(b_align_crop_tenor_list, swap_result_list, b_mat_list, crop_size, img_b_whole, logoclass, \
                          os.path.join(opt.output_path, 'result_whole_swapsingle#{framrCount}.jpg'), opt.no_simswaplogo,pasring_model =net,use_mask=opt.use_mask, norm = spNorm)

                      #print(frameCount)
                    else:
                        isEncoded, encodedImage = cv2.imencode(".jpg", img_b_whole)
                        if isEncoded:
                            outputFrame = encodedImage
                        else:
                            outputFrame = encodedPlaceholder
        except ConnectionError:
            capture.release()
            camera_connected = False
            print("Retrying connection to stream in",str(RECONNECTION_TIMEOUT),"seconds...")
            time.sleep(RECONNECTION_TIMEOUT)
        capture.release()
        print('************ Done ! ************')


def video_swap(video_path, id_vetor, swap_model, detect_model, save_path, temp_results_dir='./temp_results', crop_size=224, no_simswaplogo=False, use_mask=False):
    video = cv2.VideoCapture(video_path)
    logoclass = watermark_image('./simswaplogo/simswaplogo.png')
    ret = True

    spNorm = SpecificNorm()
    if use_mask:
        n_classes = 19
        net = BiSeNet(n_classes=n_classes)
        net.cuda()
        save_pth = os.path.join('./parsing_model/checkpoint', '79999_iter.pth')
        net.load_state_dict(torch.load(save_pth))
        net.eval()
    else:
        net =None

    while ret:
    #for frame_index in tqdm(range(frame_count)):
        ret, frame = video.read()
        if  ret:
            detect_results = detect_model.get(frame,crop_size)

            if detect_results is not None:
                # print(frame_index)
                #if not os.path.exists(temp_results_dir):
                #        os.mkdir(temp_results_dir)
                frame_align_crop_list = detect_results[0]
                frame_mat_list = detect_results[1]
                swap_result_list = []
                frame_align_crop_tenor_list = []
                for frame_align_crop in frame_align_crop_list:

                    # BGR TO RGB
                    # frame_align_crop_RGB = frame_align_crop[...,::-1]

                    frame_align_crop_tenor = _totensor(cv2.cvtColor(frame_align_crop,cv2.COLOR_BGR2RGB))[None,...].cuda()

                    swap_result = swap_model(None, frame_align_crop_tenor, id_vetor, None, True)[0]
                    #cv2.imwrite(os.path.join(temp_results_dir, 'frame_{:0>7d}.jpg'.format(frame_index)), frame)
                    swap_result_list.append(swap_result)
                    frame_align_crop_tenor_list.append(frame_align_crop_tenor)



                outputFrame = reverse2wholeimage(frame_align_crop_tenor_list,swap_result_list, frame_mat_list, crop_size, frame, logoclass, null ,no_simswaplogo,pasring_model =net,use_mask=use_mask, norm = spNorm)

            else:
                if not no_simswaplogo:
                    frame = logoclass.apply_frames(frame)
                isEncoded, encodedImage = cv2.imencode(".jpg", frame)
                if isEncoded:
                    outputFrame = encodedImage
                else:
                    outputFrame = encodedPlaceholder

               #cv2.imwrite(os.path.join(temp_results_dir, 'frame_{:0>7d}.jpg'.format(frame_index)), frame)
        else:
            break

    #release on stop
    #video.release()
    path = os.path.join(temp_results_dir,'*.jpg')
    image_filenames = sorted(glob.glob(path))


def generate():
    global outputFrame, lock

    while True:
        with lock:
            if outputFrame is None:
                continue

            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                  bytearray(outputFrame) + b'\r\n')

def stream():
    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")

def stop():
    global is_started
    is_started = False
    return {"success": True}

def start(opt):
    global is_started
    start_epoch, epoch_iter = 1, 0
    crop_size = opt.crop_size

    torch.nn.Module.dump_patches = True
    if crop_size == 512:
        opt.which_epoch = 550000
        opt.name = '512'
        mode = 'ffhq'
    else:
        mode = 'None'
    model = create_model(opt)
    model.eval()
    app = Face_detect_crop(name='antelope', root='./insightface_func/models')
    app.prepare(ctx_id=0, det_thresh=0.6, det_size=(640, 640), mode=mode)
    is_started = True
    t = threading.Thread(target=streamer, args=(app, model, opt,))
    t.daemon = True
    t.start()
    return {"success": True}
