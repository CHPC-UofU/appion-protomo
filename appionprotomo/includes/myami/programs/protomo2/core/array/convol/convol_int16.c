/*----------------------------------------------------------------------------*
*
*  convol_int16.c  -  array: operations for data type int16
*
*-----------------------------------------------------------------------------*
*
*  Copyright � 2012 Hanspeter Winkler
*
*  This software is distributed under the terms of the GNU General Public
*  License version 3 as published by the Free Software Foundation.
*
*----------------------------------------------------------------------------*/

#include "convol.h"
#include "exception.h"


#define TYPE     int16_t
#define TYPEMIN  INT16_MIN
#define TYPEMAX  INT16_MAX


/* functions */

extern Status Convol2dInt16
              (const Size *srclen,
               const void *srcaddr,
               const Size *krnlen,
               const Real *krnaddr,
               void *dstaddr)

#include "convol_2d.h"


extern Status Convol3dInt16
              (const Size *srclen,
               const void *srcaddr,
               const Size *krnlen,
               const Real *krnaddr,
               void *dstaddr)

#include "convol_3d.h"
