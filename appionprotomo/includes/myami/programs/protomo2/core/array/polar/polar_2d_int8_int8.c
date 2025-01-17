/*----------------------------------------------------------------------------*
*
*  polar_2d_int8_int8.h  -  array: spatial polar transformations
*
*-----------------------------------------------------------------------------*
*
*  Copyright � 2012 Hanspeter Winkler
*
*  This software is distributed under the terms of the GNU General Public
*  License version 3 as published by the Free Software Foundation.
*
*----------------------------------------------------------------------------*/

#include "polar.h"
#include "exception.h"
#include "mathdefs.h"


/* functions */

extern Status Polar2dInt8Int8
              (const Size *srclen,
               const void *srcaddr,
               const Coord *A,
               const Coord *b,
               const Size *dstlen,
               void *dstaddr,
               const Coord *c,
               const TransformParam *param)

#define SRCTYPE int8_t
#define DSTTYPE int8_t

#define DSTTYPEMIN (INT8_MIN)
#define DSTTYPEMAX (INT8_MAX)

#include "polar_2d.h"
