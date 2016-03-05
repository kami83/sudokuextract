#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
corners
==================

Created by: hbldh <henrik.blidh@nedomkull.com>
Created on: 2016-03-05, 13:09

"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import numpy as np

from dlxsudoku.sudoku import Sudoku

from sudokuextract.exceptions import SudokuExtractError
from sudokuextract.imgproc.blob import iter_blob_extremes
from sudokuextract.imgproc import geometry
from sudokuextract.ml.predict import classify_sudoku
from sudokuextract.utils import predictions_to_suduko_string


def extraction_method_corners(image, classifier, use_local_thresholding=False, n=5):
    for sudoku, subimage in _extraction_iterator_corners(image, use_local_thresholding, n=n):
        try:
            pred_n_imgs = classify_sudoku(sudoku, classifier, False)
            preds = np.array([[pred_n_imgs[k][kk][0] for kk in range(9)] for k in range(9)])
            imgs = [[pred_n_imgs[k][kk][1] for kk in range(9)] for k in range(9)]
            if np.sum(preds > 0) >= 17:
                s = Sudoku(predictions_to_suduko_string(preds))
                try:
                    s.solve()
                except Exception:
                    pass
                else:
                    return preds, imgs, subimage
        except Exception as e:
            pass
    raise SudokuExtractError("Corner Method could not extract any Sudoku from this image.")


def _extraction_iterator_corners(image, use_local_thresholding=False, n=5):
    img = image.convert('L')
    # If the image is too small, then double its scale until big enough.
    while max(img.size) < 500:
        img = img.resize(np.array(img.size) * 2)
    for corner_points in iter_blob_extremes(img, n=n):
        try:
            warped_image = geometry.warp_image_by_corner_points_projection(corner_points, img)
            sudoku, bin_image = geometry.split_image_into_sudoku_pieces_adaptive_global(
                warped_image, otsu_local=use_local_thresholding)
        except SudokuExtractError:
            # Try next blob.
            pass
        except Exception as e:
            raise
        else:
            yield sudoku, bin_image