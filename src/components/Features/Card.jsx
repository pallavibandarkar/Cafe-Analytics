import {
    Card,
    CardHeader,
    CardBody,
    CardFooter,
    Typography,
    Button,
  } from "@material-tailwind/react";
  
  export function CardDefault({ imageSrc, title, description }) {
    return (
      <Card className="mt-6 w-full max-w-xs">
        <CardHeader floated={false} className="relative h-55">
          <img
            src={imageSrc}
            alt="card-image"
           
            className="object-cover w-full h-full"
          />
        </CardHeader>
        <CardBody>
          <Typography variant="h5" color="blue-gray" className="mb-2">
            {title}
          </Typography>
          <Typography>
            {description}
          </Typography>
        </CardBody>
        <CardFooter className="pt-0">
          <Button>Read More</Button>
        </CardFooter>
      </Card>
    );
  }
  