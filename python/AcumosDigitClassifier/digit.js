/*
  ===============LICENSE_START=======================================================
  Acumos Apache-2.0
  ===================================================================================
  Copyright (C) 2017-2019 AT&T Intellectual Property & Tech Mahindra. All rights reserved.
  ===================================================================================
  This Acumos software file is distributed by AT&T and Tech Mahindra
  under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

  This file is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
  ===============LICENSE_END=========================================================
*/

/*
 * digit.js -- Javascript code from Web demo of Acumos Handwritten Digit Recognition Model
 *
 * Guy Jacobson, 4/8/2018
 */

// Protobuf messages for input and output
var predictIn;
var predictOut;

// Load protobuf description created when model was dumped
protobuf.load('model.proto')
    .then(function(root) {
        predictIn = root.lookup('PredictIn');
	predictOut = root.lookup('PredictOut');
    });


// Drawing code

var context;
var pcontext;
var mouseIsDown;
var xCoord;
var yCoord;
var mouseState;
var prediction;  // boolean: has a prediction been made on the current image?

function initCanvas() {
    context = document.getElementById('canvas').getContext('2d');
    context.strokeStyle = 'black';
    context.fillStyle = 'white';
    context.lineJoin = 'round';
    context.lineCap = 'round';
    context.lineWidth = 15;

    pcontext = document.getElementById('prediction').getContext('2d');
    pcontext.font = '240px Roboto';
    pcontext.textAlign = 'center';
    pcontext.textBaseline = 'middle';

    $('#canvas').mousedown(function (e) {
        if (prediction)
            clearCanvas();
        addPoint(e.pageX - this.offsetLeft, e.pageY - this.offsetTop);
        mouseIsDown = true;
        redraw();
    });

    $('#canvas').mousemove(function (e) {
        if (mouseIsDown) {
            addPoint(e.pageX - this.offsetLeft, e.pageY - this.offsetTop);
            redraw();
        }
    });

    $('#canvas').mouseup(function (e) {
        mouseIsDown = false;
    });

    $('#canvas').mouseleave(function (e) {
        mouseIsDown = false;
    });

    clearCanvas();
}

function addPoint(x, y) {
    if (prediction)
        clearPrediction();
    xCoord.push(x);
    yCoord.push(y);
    mouseState.push(mouseIsDown);
}

function clearCanvas() {
    mouseIsDown = false;
    xCoord = new Array();
    yCoord = new Array();
    mouseState = new Array();
    prediction = false;
    context.fillRect(0, 0, 280, 280);
    clearPrediction();
}

function redraw() {
    context.fillRect(0, 0, 280, 280);

    context.beginPath();

    for (var i = 0; i < xCoord.length; i++) {
        if (mouseState[i])
            context.lineTo(xCoord[i], yCoord[i]);
        else
            context.moveTo(xCoord[i], yCoord[i]);
    }

    context.stroke();
}

function clearPrediction() {
    pcontext.fillStyle = 'grey';
    pcontext.fillRect(0, 0, 280, 280);
    prediction = false;
}

function setPrediction(p) {
    pcontext.fillStyle = 'white';
    pcontext.fillRect(0, 0, 280, 280);
    pcontext.fillStyle = 'black';
    pcontext.fillText(p, 140, 160);
    prediction = true;
}

// Called when user clicks the "Recognize" button
function recognize() {
    var canvas = document.getElementById('canvas');
    canvas.toBlob(function (blob) {
        var f = new FileReader();
        f.onload = function (e) {
            var uint8array = new Uint8Array(e.target.result)
            var message = predictIn.create({
                imdata: uint8array
            });
            var encMessage = predictIn.encode(message).finish();
            var url = $('#url').val();
            $.ajax({
                url: url,
                type: 'POST',
                data: encMessage,
                contentType: 'text/plain', // not really correct, but needed to avoid CORS issues
                processData: false,
                dataFilter: function (s, t) {
                    var buf = new Uint8Array(s.length);
                    for (var i = 0; i < s.length; i++)
                        buf[i] = s.charCodeAt(i);
                    var response = predictOut.decode(buf);
                    return response['value'];
                },
                success: function (result, s, x) {
                    setPrediction(result);
                },
                error: function () {}
            });
        }
        f.readAsArrayBuffer(blob);
    });
}
