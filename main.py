import shotstack_sdk as shotstack
from shotstack_sdk.api import edit_api
from shotstack_sdk.model import *

# Initialize Shotstack API
API_KEY = "your_api_key_here"  # Replace with your Shotstack API Key
configuration = shotstack.Configuration(host="https://api.shotstack.io/v1")
configuration.api_key["x-api-key"] = API_KEY

# Create an API client
with shotstack.ApiClient(configuration) as api_client:
    api_instance = edit_api.EditApi(api_client)

    # Define Images
    image1 = ImageAsset(src="https://your-image-url1.jpg")  # Replace with your image URL
    image2 = ImageAsset(src="https://your-image-url2.jpg")

    # Apply Effects (Zoom-in for Image 1)
    clip1 = Clip(
        asset=image1,
        start=0.0,
        length=3.0,  # Display for 3 seconds
        effect="zoomInSlow"  # Apply zoom-in effect
    )

    # Image 2 with blur transition
    clip2 = Clip(
        asset=image2,
        start=3.0,  # Start after the first image
        length=3.0,
        transition=Transition(
            _in="blur",  # Apply blur transition
            out="blur"
        )
    )

    # Arrange clips in timeline
    track1 = Track(clips=[clip1, clip2])
    timeline = Timeline(tracks=[track1])

    # Output settings
    output = Output(format="mp4", resolution="hd")

    # Create render request
    edit = Edit(timeline=timeline, output=output)

    # Send request to render video
    try:
        response = api_instance.post_render(edit)
        # Print Render ID
        print(f"Render ID: {response.id}")
        print("Check Shotstack Dashboard to view progress.")
    except shotstack.ApiException as e:
        print(f"An error occurred: {e}")
