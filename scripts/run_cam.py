if __name__ == '__main__':
    import pygame
    import subprocess as sp
    from PIL import Image
    import pygame
    import time
    import cv2
    import scipy.misc
    import threading

    pygame.init()
    size=(640,480)
    ssize=(1280,480)
    screen = pygame.display.set_mode(ssize)
    im1_1= pygame.Surface((320,240))
    im1_2= pygame.Surface((320,240))

    cam_conf = config.camera_parser_config('camera_1.ini')
    cam_1 = Camera('cam_1', cam_conf)
    cam_conf = config.camera_parser_config('camera_2.ini')
    cam_2 = Camera('cam_2', cam_conf)

    import numpy
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        image1 = cam_1.image
        image2 = cam_2.image
        pygame.pixelcopy.array_to_surface(im1_1, image1)
        pygame.pixelcopy.array_to_surface(im1_2, image2)
        im2_1 = pygame.transform.scale(im1_1,size)
        im2_2 = pygame.transform.scale(im1_2,size)
        screen.blit(im2_1,(0,0))
        screen.blit(im2_2,(size[0],0))
        pygame.display.flip()
        cv2.imwrite('test1.bmp', image1)
        cv2.imwrite('test2.bmp', image2)
    cam_1.stop()
    cam_2.stop()
    pygame.quit()