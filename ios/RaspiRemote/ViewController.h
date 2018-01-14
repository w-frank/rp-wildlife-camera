//
//  ViewController.h
//  RasPiRemote
//
//  Created by Will Frank on 02/12/2017.
//  Copyright (c) 2017 Will Frank. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "MobileVLCKit/MobileVLCKit.h"

@interface ViewController : UIViewController <NSStreamDelegate> {
    BOOL _connectInProgress;
    NSOutputStream *_outputStream;
    NSString *streamStatus;
    NSString *motionStatus;
}

@property(nonatomic, strong) IBOutlet UITextField *host;
@property(nonatomic, strong) IBOutlet UITextField *port;
@property(nonatomic, strong) IBOutlet UIButton *connect;
@property(nonatomic, strong) IBOutlet UIButton *disconnect;
@property(nonatomic, strong) IBOutlet UIButton *stream;
@property(nonatomic, strong) IBOutlet UIButton *motion;
@property(nonatomic, strong) IBOutlet UILabel *status;
@property(nonatomic, strong) IBOutlet UIView *videoView;
@property (nonatomic, retain) NSString *streamStatus;
@property (nonatomic, retain) NSString *motionStatus;
@property VLCMediaPlayer *mediaPlayer;

- (IBAction)doConnect:(id)sender;
- (IBAction)doDisconnect:(id)sender;

- (IBAction)turnLeft:(id)sender;
- (IBAction)turnRight:(id)sender;

- (IBAction)stop:(id)sender;

@end
