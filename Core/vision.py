import cv2

class Vision:

    def __init__(self):
        pass

    def get_priority_target(self, boxes):
        max_bb_area = 0
        target = None
        for box in boxes:
            if box[5] == 0 and box[4] > 0.45:
                xB = int(box[2]-25)
                xA = int(box[0]+25)
                yB = int(box[3]-25)
                yA = int(box[1]+25)

                if (xB - xA) * (yB - yA) > max_bb_area:
                    max_bb_area = (xB - xA) * (yB - yA)
                    target = self.getCenter(xA, yA, xB, yB, 0.1)
        return target

    def draw_bounding_boxes(self, frame, boxes):
        for box in boxes:
            if box[5] == 0 and box[4] > 0.45:
                xB = int(box[2])
                xA = int(box[0])
                yB = int(box[3])
                yA = int(box[1])

                cv2.rectangle(frame, (xA, yA), (xB, yB), (0, 255, 0), 2)
                cv2.putText(frame, f"{box[4]: .2f}", (xA,yA-10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
        return frame

    def getCenter(self, xA, yA, xB, yB, offset):
        return (int((xA + xB)/2), int(yA - (offset * (yA - yB)))+30)